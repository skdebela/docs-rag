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
from app.log_utils import safe_log_gotcha

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

from fastapi import Header

@app.post("/api/admin/clear_all")
def clear_all(admin_token: str = Header(..., alias="admin-token"), db: Session = Depends(get_db)):
    """
    Danger: Delete ALL files and chat history from DB and vectorstore. Requires admin-token header.
    """
    ADMIN_TOKEN = os.environ.get("CHAT_RAG_ADMIN_TOKEN", "supersecret")
    if admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Delete all chat history
    chat_count = db.query(ChatHistory).delete()
    # Delete all files
    file_count = db.query(DBFile).delete()
    db.commit()
    # Delete all embeddings from vectorstore
    try:
        vec_data = rag_pipeline.vectorstore.get()
        all_ids = vec_data.get('ids', [])
        if all_ids:
            rag_pipeline.vectorstore.delete(ids=all_ids)
        from app.rag.pipeline import RAGPipeline
        rag_pipeline.vectorstore = RAGPipeline(vector_db_path=rag_pipeline.vector_db_path).vectorstore
        safe_log_gotcha(f"[AdminClearAll] All files and chats deleted at {datetime.now().isoformat()}")
    except Exception as e:
        safe_log_gotcha(f"[AdminClearAll] Vectorstore clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vectorstore clear failed: {e}")
    return {"status": "cleared", "files_deleted": file_count, "chats_deleted": chat_count}

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
    """
    Delete a file: always removes from DB, attempts vectorstore and disk deletion.
    Returns success unless DB record is missing. Errors in vectorstore/disk removal are returned as warnings.
    Logs all errors and operational events to gotchas.md (see log_utils.safe_log_gotcha).
    """
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    errors = []
    # Try to remove from vectorstore by document metadata (Chroma API does not support filter, so log gotcha and skip)
    try:
        # Chroma delete only supports ids (list of doc ids) or where (dict for metadata match)
        # We'll use where if supported, otherwise log gotcha
        rag_pipeline.vectorstore.delete(where={"file_id": file_id})
        # Re-initialize vectorstore to clear any in-memory cache
        from app.rag.pipeline import RAGPipeline
        rag_pipeline.vectorstore = RAGPipeline(vector_db_path=rag_pipeline.vector_db_path).vectorstore
    except Exception as e:
        errors.append(f"Vectorstore delete by file_id (where) error: {e}")
        safe_log_gotcha(f"[DeleteFile] Chroma delete API mismatch or failure: {e}")
    try:
        rag_pipeline.vectorstore.delete(where={"filename": db_file.filename})
        from app.rag.pipeline import RAGPipeline
        rag_pipeline.vectorstore = RAGPipeline(vector_db_path=rag_pipeline.vector_db_path).vectorstore
    except Exception as e:
        errors.append(f"Vectorstore delete by filename (where) error: {e}")
        safe_log_gotcha(f"[DeleteFile] Chroma delete API mismatch or failure: {e}")
    # Try to remove from disk
    try:
        os.remove(db_file.filepath)
    except FileNotFoundError:
        pass
    except Exception as e:
        errors.append(f"File delete error: {e}")
    # Always remove DB record
    db.delete(db_file)
    db.commit()
    if errors:
        # Log all errors for traceability and compliance
        for err in errors:
            safe_log_gotcha(f"[DeleteFile] {err}")
    else:
        # Log successful deletion event
        safe_log_gotcha(f"[DeleteFile] File {file_id} deleted successfully at {datetime.now().isoformat()}")
    return {"status": "deleted", "warnings": errors}


@app.post("/api/chat")
def chat(question: str = Query(...), file_id: int = Query(None), db: Session = Depends(get_db)):
    """
    Chat endpoint: if no files in DB, do not answer from vectorstore and return a clear message. Log the event to gotchas.md for traceability.
    """
    db_files = db.query(DBFile).all()
    if not db_files:
        safe_log_gotcha(f"[Chat] No files in DB at {datetime.now().isoformat()}")
        return {"answer": "No files are available for answering. Please upload a file first.", "sources": []}
    # Always retrieve from all loaded files (all in DB)
    docs = rag_pipeline.retrieve(question, k=4)
    # Filter docs so only those whose file_id is present in the current DB are used
    current_file_ids = {str(f.id) for f in db_files}
    docs = [d for d in docs if str(d.metadata.get("file_id")) in current_file_ids]
    # Construct context
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    # Call LLM (Ollama)
    try:
        answer = ollama_llm.invoke(prompt)
    except Exception as e:
        safe_log_gotcha(f"[Chat] LLM inference failed: {str(e)} at {datetime.now().isoformat()}")
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
