import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db, init_db
from app.db.models import File as DBFile, ChatHistory
from app.rag.pipeline import RAGPipeline, SUPPORTED_EXTENSIONS
from datetime import datetime
import shutil
import uuid

# Use langchain-ollama for LLM integration (future-proof)
from langchain_ollama import OllamaLLM
ollama_llm = OllamaLLM(model="mistral")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/files"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Local-First RAG Chat App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB and RAG pipeline
init_db()
rag_pipeline = RAGPipeline(vector_db_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma_db")))

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    file_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db_file = DBFile(
        filename=file.filename,
        filepath=save_path,
        upload_time=datetime.utcnow(),
        file_metadata="{}"
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    # Ingest into RAG pipeline
    try:
        rag_pipeline.ingest(save_path, metadata={"file_id": db_file.id, "filename": db_file.filename})
    except Exception as e:
        db.delete(db_file)
        db.commit()
        os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"RAG ingestion failed: {str(e)}")
    return {"id": db_file.id, "filename": db_file.filename}

@app.get("/api/files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(DBFile).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "upload_time": f.upload_time.isoformat(),
            "file_metadata": f.file_metadata
        }
        for f in files
    ]

@app.delete("/api/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    # Remove from vectorstore (not strictly required, but good hygiene)
    try:
        rag_pipeline.vectorstore.delete([str(file_id)])
    except Exception:
        pass  # Log if needed
    # Remove from disk
    try:
        os.remove(db_file.filepath)
    except FileNotFoundError:
        pass
    db.delete(db_file)
    db.commit()
    return {"status": "deleted"}

@app.post("/api/chat")
def chat(question: str = Query(...), file_id: int = Query(None), db: Session = Depends(get_db)):
    # Retrieve relevant docs (all files or filtered by file_id)
    if file_id:
        db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        docs = rag_pipeline.retrieve(question, k=4)
        # Optionally filter docs by file_id metadata
        docs = [d for d in docs if str(d.metadata.get("file_id")) == str(file_id)]
    else:
        docs = rag_pipeline.retrieve(question, k=4)
    # Construct context
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    # Call LLM (Ollama)
    try:
        answer = ollama_llm.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM inference failed: {str(e)}")
    # Log chat history
    chat = ChatHistory(
        user_id=None,
        file_id=file_id,
        question=question,
        answer=answer,
        timestamp=datetime.utcnow()
    )
    db.add(chat)
    db.commit()
    return {"answer": answer, "sources": [d.metadata for d in docs]}
