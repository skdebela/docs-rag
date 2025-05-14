import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db, init_db
from app.db.models import File as DBFile, ChatHistory
from app.rag.pipeline import RAGPipeline, SUPPORTED_EXTENSIONS
from datetime import datetime
import shutil
import uuid
from app.log_utils import safe_log_gotcha
from app.schemas import FileUploadResponse, FileListItem, ChatResponse, AdminClearAllResponse
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import time

# Get Google API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    convert_system_message_to_human=True,
    temperature=0.7,
    max_output_tokens=2048,
)

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/files"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="RAG Chat App")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized error handlers
from app.error_handlers import http_exception_handler, sqlalchemy_exception_handler, generic_exception_handler
from sqlalchemy.exc import SQLAlchemyError
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "./data/chroma_db"))
os.makedirs(CHROMA_PATH, exist_ok=True)

# Initialize DB and RAG pipeline
init_db()
rag_pipeline = RAGPipeline(vector_db_path=CHROMA_PATH, api_key=GOOGLE_API_KEY)

from fastapi import Header

from app.services.admin_service import clear_all_service

@app.post("/api/admin/clear_all", response_model=AdminClearAllResponse)
def clear_all(admin_token: str = Header(..., alias="admin-token", min_length=8, max_length=128), db: Session = Depends(get_db)) -> AdminClearAllResponse:
    """
    Danger: Delete ALL files and chat history from DB and vectorstore. Delegates business logic to admin_service.
    Validates admin token length (8-128 chars).
    """
    ADMIN_TOKEN = os.environ.get("CHAT_RAG_ADMIN_TOKEN", "supersecret")
    if not (admin_token.isalnum() or '-' in admin_token or '_' in admin_token):
        raise HTTPException(status_code=422, detail="Invalid admin token format.")
    return AdminClearAllResponse(**clear_all_service(
        admin_token=admin_token,
        db=db,
        rag_pipeline=rag_pipeline,
        admin_env_token=ADMIN_TOKEN
    ))


@app.get("/api/health")
def health_check():
    """
    Health check endpoint: verifies DB, vectorstore, and LLM health.
    """
    # DB health
    try:
        db_ok = True
        db_msg = "OK"
        session_gen = get_db()
        session = next(session_gen)
        session.execute(text("SELECT 1"))
        session.close()
    except Exception as e:
        db_ok = False
        db_msg = str(e)
    # Vectorstore health
    try:
        vec_ok = True
        vec_msg = "OK"
        _ = rag_pipeline.vectorstore.get()
    except Exception as e:
        vec_ok = False
        vec_msg = str(e)
    # LLM health
    try:
        llm_ok = True
        llm_msg = "OK"
        _ = gemini_llm.invoke("Health check?")
        llm_model = "gemini-2.0-flash"
    except Exception as e:
        llm_ok = False
        llm_msg = str(e)
        llm_model = "gemini-2.0-flash"
    status = "ok" if all([db_ok, vec_ok, llm_ok]) else "degraded"
    return {
        "status": status,
        "db": {"ok": db_ok, "msg": db_msg},
        "vectorstore": {"ok": vec_ok, "msg": vec_msg},
        "llm": {"ok": llm_ok, "msg": llm_msg, "model": llm_model}
    }

from app.services.file_service import upload_file as upload_file_service

@app.post("/api/upload", response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> FileUploadResponse:
    """
    Upload a file and ingest into the RAG pipeline. Delegates business logic to file_service.
    Validates file extension against SUPPORTED_EXTENSIONS.
    """
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {ext}")
    db_file = upload_file_service(file=file, db=db)
    # Ingest into RAG pipeline (kept here to avoid circular dependency)
    try:
        rag_pipeline.ingest(db_file.filepath, metadata={"file_id": db_file.id, "filename": db_file.filename})
    except Exception as e:
        db.delete(db_file)
        db.commit()
        os.remove(db_file.filepath)
        raise HTTPException(status_code=500, detail=f"RAG ingestion failed: {str(e)}")
    return FileUploadResponse(id=db_file.id, filename=db_file.filename)


from app.services.file_service import list_files as list_files_service

@app.get("/api/files", response_model=list[FileListItem])
def list_files(db: Session = Depends(get_db)) -> list[FileListItem]:
    """
    List all files in the database. Delegates business logic to file_service.
    """
    files = list_files_service(db=db)
    return [
        FileListItem(
            id=f.id,
            filename=f.filename,
            upload_time=f.upload_time,
            file_metadata=f.file_metadata
        ) for f in files
    ]

from app.services.file_service import delete_file as delete_file_service

@app.delete("/api/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Delete a file: removes from DB and disk, attempts vectorstore cleanup. Delegates business logic to file_service for DB/disk, keeps vectorstore logic here to avoid circular dependency.
    """
    # Remove from DB and disk
    result = delete_file_service(file_id=file_id, db=db)
    # Remove from vectorstore
    errors = result.get("warnings", [])
    try:
        rag_pipeline.vectorstore.delete(where={"file_id": file_id})
        from app.rag.pipeline import RAGPipeline
        rag_pipeline.vectorstore = RAGPipeline(vector_db_path=rag_pipeline.vector_db_path).vectorstore
    except Exception as e:
        errors.append(f"Vectorstore delete by file_id (where) error: {e}")
        safe_log_gotcha(f"[DeleteFile] Chroma delete API mismatch or failure: {e}")
    try:
        # Try by filename (if file still exists)
        db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
        if db_file:
            rag_pipeline.vectorstore.delete(where={"filename": db_file.filename})
            from app.rag.pipeline import RAGPipeline
            rag_pipeline.vectorstore = RAGPipeline(vector_db_path=rag_pipeline.vector_db_path).vectorstore
    except Exception as e:
        errors.append(f"Vectorstore delete by filename (where) error: {e}")
        safe_log_gotcha(f"[DeleteFile] Chroma delete API mismatch or failure: {e}")
    return {"status": "deleted", "warnings": errors}



from app.services.chat_service import chat_service

from app.schemas import ChatRequest

@app.post("/api/chat", response_model=ChatResponse)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def chat(
    chat_req: ChatRequest = None,
    question: str = Query(None, min_length=3, max_length=500),
    file_id: int = Query(None),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat endpoint: supports hybrid retrieval (keywords, metadata, MMR, k). Accepts ChatRequest body or legacy query params.
    Handles rate limits with retries.
    """
    # Prefer body if provided, else fallback to query params for legacy clients
    if chat_req is not None:
        req = chat_req
    else:
        req = ChatRequest(question=question, file_id=file_id)
    try:
        return ChatResponse(**chat_service(
            question=req.question,
            file_id=req.file_id,
            db=db,
            rag_pipeline=rag_pipeline,
            llm=gemini_llm,
            keywords=req.keywords,
            metadata_filter=req.metadata_filter,
            k=req.k
        ))
    except Exception as e:
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            safe_log_gotcha(f"[Chat] Rate limit hit, retrying: {e}")
            raise  # Retry
        raise HTTPException(status_code=500, detail=str(e))
