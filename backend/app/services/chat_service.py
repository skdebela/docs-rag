from sqlalchemy.orm import Session
from app.db.models import File as DBFile, ChatHistory
from app.log_utils import safe_log_gotcha
from datetime import datetime
from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import time

# The rag_pipeline and ollama_llm must be injected by the caller to avoid circular imports.
def chat_service(
    question: str,
    file_id: Optional[int],
    db: Session,
    rag_pipeline,
    llm,
    keywords: Optional[list] = None,
    metadata_filter: Optional[dict] = None,
    k: Optional[int] = 4
) -> Dict[str, Any]:
    """
    Handles chat logic: retrieves relevant docs (hybrid/vector/keyword/MMR), constructs prompt, calls LLM, logs history.
    Includes rate limit handling and retries.
    """
    db_files = db.query(DBFile).all()
    if not db_files:
        safe_log_gotcha(f"[Chat] No files in DB at {datetime.now().isoformat()}")
        return {"answer": "No files are available for answering. Please upload a file first.", "sources": []}
    # Metadata filter by file_id if provided
    if file_id:
        if metadata_filter is None:
            metadata_filter = {}
        metadata_filter["file_id"] = file_id
    docs = rag_pipeline.retrieve(
        question,
        k=k,
        keywords=keywords,
        metadata_filter=metadata_filter
    )
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
    
    # Call LLM with retry for rate limits
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_llm_response():
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                safe_log_gotcha(f"[Chat] Rate limit hit, retrying: {e}")
                time.sleep(1)  # Rate limit protection
                raise  # Retry
            raise HTTPException(status_code=500, detail=f"LLM inference failed: {str(e)}")
    
    try:
        answer = get_llm_response()
        # Extract content from AIMessage
        answer_content = answer.content if hasattr(answer, 'content') else str(answer)
    except Exception as e:
        safe_log_gotcha(f"[Chat] LLM inference failed after retries: {str(e)} at {datetime.now().isoformat()}")
        raise HTTPException(status_code=500, detail=f"LLM inference failed after retries: {str(e)}")
    
    # Log chat history
    chat = ChatHistory(
        user_id=None,
        file_id=file_id,
        question=question,
        answer=answer_content,
        timestamp=datetime.utcnow()
    )
    db.add(chat)
    db.commit()
    # Only show unique document names in sources
    import os, re
    # Count occurrences of each file among retrieved docs
    file_counts = {}
    for d in docs:
        name = d.metadata.get('source') or d.metadata.get('filename') or d.metadata.get('file_name')
        if name:
            base = os.path.basename(name)
            base = re.sub(r'^[0-9a-fA-F-]+_', '', base)
        else:
            base = 'Unknown File'
        file_counts[base] = file_counts.get(base, 0) + 1
    # Find the file with the most chunks in the answer
    if file_counts:
        most_relevant_file = max(file_counts, key=file_counts.get)
    else:
        most_relevant_file = 'Unknown File'
    return {"answer": answer_content, "sources": [most_relevant_file]}
