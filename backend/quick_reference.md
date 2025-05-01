# Quick Reference

## API Endpoints
- `POST   /api/upload`    (file upload)
- `GET    /api/files`     (list files)
- `DELETE /api/files/{file_id}` (delete file)
- **POST /api/chat**
  - Query with a question (3-500 chars)
  - Request body (preferred):
    ```json
    {
      "question": "What are the main findings?",
      "file_id": 1,
      "keywords": ["finding", "summary"],
      "metadata_filter": {"section": "Results"},
      "k": 8
    }
    ```
  - Query params (legacy support): `question: str`, `file_id: int (optional)`
  - Response: `{ answer, sources }`
  - Supports hybrid retrieval: vector + keyword + metadata, strict top-k retrieval (no MMR), and adaptive chunking.
  - **Frontend:** Advanced retrieval options (keywords, metadata, k) are supported in the API client and state store. The UI can be extended to let users set keywords, filters, or k.
- `GET    /api/health`    (health check)

## Vectorstore Persistence
- Chroma persistence is automatic with `persist_directory` (no `.persist()` method needed).

<!-- Add Docker/database persistence instructions here -->

## Frontend Support
- The frontend API client and chat state store now support all advanced hybrid retrieval options:
    - `keywords`, `metadata_filter`, `use_mmr`, `k`
- Backwards compatible: legacy chat flows (question/file_id only) still work.
- The UI can be extended to let users set these options directly.
- No breaking changes for existing chat or file flows.

## Modular RAG Pipeline (2025)
- Uses only `RecursiveCharacterTextSplitter` for chunking (no NLTK, no punkt, no spaCy).
- Advanced retrieval: top-k, metadata filtering, ready for hybrid search.
- Rich metadata on every chunk (filename, section, etc.).
- Prompt engineering: clear system prompt, context, user question.
- Async and streaming support (where possible).
- Comprehensive logging for debugging and evaluation.

### Usage Example
```python
from app.rag.pipeline_modular import ModularRAGPipeline
pipeline = ModularRAGPipeline()
pipeline.ingest('/path/to/file.pdf', metadata={'uploaded_by': 'user1'})
result = pipeline.chat('What are the main findings?', k=6)
print(result['answer'])
```

## Required Dependencies
- `langchain_chroma`
- `unstructured` (for docx/xlsx parsing)
- `ollama` (must be running locally for embeddings/LLM)

## Frontend Dev
- Vite proxy forwards `/api` to backend on `localhost:8000` (see `vite.config.ts`).
