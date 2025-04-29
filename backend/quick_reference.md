# Quick Reference

## API Endpoints
- `POST   /api/upload`    (file upload)
- `GET    /api/files`     (list files)
- `DELETE /api/files/{file_id}` (delete file)
- `POST   /api/chat`      (chat with RAG)
- `GET    /api/health`    (health check)

## Vectorstore Persistence
- Chroma persistence is automatic with `persist_directory` (no `.persist()` method needed).

## Required Dependencies
- `langchain_chroma`
- `unstructured` (for docx/xlsx parsing)
- `ollama` (must be running locally for embeddings/LLM)

## Frontend Dev
- Vite proxy forwards `/api` to backend on `localhost:8000` (see `vite.config.ts`).
