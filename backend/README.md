# Backend for Local-First RAG Chat App

_Last updated: 2025-04-29_

## Purpose
This backend implements a privacy-preserving, local-first Retrieval-Augmented Generation (RAG) chat application. All data, files, and models are processed and stored **locally**—no cloud dependencies.

---

## Architecture Overview

- **API Framework:** FastAPI (Python)
- **RAG Pipeline:** Langchain (file parsing, chunking, embedding, retrieval, LLM orchestration)
- **LLM & Embeddings:** Ollama (local LLM and embedding models)
- **Vector Store:** ChromaDB (local, disk-based)
- **User/File Metadata:** SQLite (via SQLAlchemy)
- **File Storage:** Local filesystem

---

## Folder Structure
```
/backend
├── app/
│   ├── main.py            # FastAPI entrypoint
│   ├── api/               # API route modules
│   ├── db/                # DB models and session
│   ├── rag/               # RAG pipeline (Langchain, Ollama, ChromaDB)
│   ├── utils/             # Utility functions
│   └── config.py          # Settings and constants
├── requirements.txt
└── README.md
```

---

## Key Features
- All user data, files, and embeddings are stored **locally**.
- No external API calls for LLM inference or embeddings.
- Modular, extensible backend for secure RAG workflows.
- SQLite is used for user and file metadata (easy to migrate to Postgres if needed).
- ChromaDB stores vector embeddings on disk.
- Ollama runs LLM and embedding models locally for privacy and speed.

---

## Endpoints (to be implemented)
- `POST /upload` — Upload a document (stores file locally, triggers embedding & vector storage)
- `POST /chat` — Ask a question (retrieves relevant chunks, queries local LLM, returns answer)
- `GET /files` — List uploaded files
- `DELETE /files/{file_id}` — Delete a file
- (Optional) Auth endpoints for multi-user setups

---

## Operational Notes
- All architectural decisions, pitfalls, and integration gotchas must be logged in `implementation_details.md` and `gotchas.md`.
- Changes to requirements or stack must be reflected in `/quick_reference.md` and referenced in commit messages.
- All code and documentation updates must be kept in sync per operational directives.

---

## Next Steps
1. Implement FastAPI app and endpoints
2. Integrate Langchain, Ollama, and ChromaDB
3. Set up SQLite models for user and file metadata
4. Test end-to-end local RAG flow
5. Document all decisions and gotchas
