from sqlalchemy.orm import Session
from app.db.models import File as DBFile, ChatHistory
from app.log_utils import safe_log_gotcha
from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

# The rag_pipeline and ollama_llm must be injected by the caller to avoid circular imports.
def chat_service(
    question: str,
    file_id: Optional[int],
    db: Session,
    rag_pipeline,
    ollama_llm
) -> Dict[str, Any]:
    """
    Handles chat logic: retrieves relevant docs, constructs prompt, calls LLM, logs history.
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
    system_prompt = (
        "You are a helpful AI assistant. Always answer in well-structured markdown. "
        "Use headings, bullet points, spacing and tables where appropriate. "
        "Format code and data for maximum readability."
        "Keep it concise and to the point."
        "If you don't know the answer, say so.\n"
    )
    prompt = f"{system_prompt}Context:\n{context}\n\nQuestion: {question}\nAnswer:"
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
