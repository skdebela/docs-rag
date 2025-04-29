# Quick Reference: Local-First RAG Chat App Requirements

_Last updated: 2025-04-29_

## Purpose
This document outlines the **requirements and architecture** for a privacy-preserving, local-first Retrieval-Augmented Generation (RAG) chat application.

---

## Key Requirements

### 1. Local Data & File Storage
- All files are stored **locally** on the server (no cloud storage).
- User data (login, API keys, file metadata) is stored in a **local database** (e.g., SQLite or Postgres).
- (Optional) Local user authentication (username/password).

### 2. Local LLM & Embeddings
- The LLM runs **locally** via [Ollama](https://ollama.com/) (e.g., Llama 3, Mistral, etc).
- Embeddings are generated **locally** (Ollama embedding models or open-source alternatives like `sentence-transformers`).
- No calls to cloud-based LLMs or embedding APIs.

### 3. Local Vector Store
- Use a **local vector database** (ChromaDB recommended; FAISS as an alternative).
- Vector DB is stored on local disk.

### 4. File Processing & RAG Pipeline
- File parsing, chunking, embedding, and storage are all performed locally.
- Use **Langchain** (Python) to orchestrate:
    - File parsing (PDF, DOCX, TXT)
    - Chunking (TextSplitter)
    - Embedding (local model)
    - Vector storage (ChromaDB)
    - Retrieval and context construction
    - LLM inference via Ollama
- No external workflow tools required for core RAG.

### 5. Frontend
- Built with Vite + React (Chakra UI or Tailwind for styling).
- Communicates with backend via REST API (localhost).

### 6. Backend
- Python with FastAPI (async, integrates with Langchain).
- Exposes endpoints for:
    - File upload (stores files locally)
    - Chat (RAG pipeline: retrieves relevant chunks, queries local LLM, returns answer)
    - File management (list, delete, etc.)
    - (Optional) Auth endpoints

---

## End-to-End Workflow
1. User uploads file via frontend.
2. Backend parses, chunks, and embeds file locally.
3. Embeddings stored in local ChromaDB, file in local filesystem, metadata in local DB.
4. User asks a question.
5. Backend retrieves relevant chunks via ChromaDB, constructs prompt.
6. LLM runs locally via Ollama, answer is generated and returned.
7. No data leaves the local machine at any point.

---

## Stack Overview
| Layer        | Technology         | Why                                    |
|--------------|--------------------|----------------------------------------|
| Frontend     | Vite + React       | Modern, fast, flexible                 |
| UI           | Chakra UI/Tailwind | Your preference                        |
| Backend      | FastAPI (Python)   | Async, integrates with Langchain       |
| File Storage | Local filesystem   | No cloud, privacy-preserving           |
| User DB      | SQLite/Postgres    | Local, easy setup                      |
| Vector Store | ChromaDB           | Local, easy Langchain integration      |
| Embeddings   | Local model        | Via Ollama or sentence-transformers    |
| LLM          | Ollama (local)     | Runs Llama/Mistral etc. locally        |
| Auth         | Local (optional)   | Username/password, no cloud            |

---

## Security & Privacy
- No data leaves the user’s machine.
- All files, embeddings, and chat history are local.
- (Optional) Add local user authentication for multi-user setups.

---

## Notes
- All requirements and architectural decisions are documented in accordance with operational directives.
- For changes, update this document and reference in commit messages.


# Quick Reference: Running ChatRAG with Docker

## 1. Prerequisites
- Docker and Docker Compose installed.

## 2. One-Command Startup
```sh
docker compose up --build
```

This will:
- Build and start all services: backend (FastAPI), frontend (Vite/React), ChromaDB, and Ollama (with `mistral:latest` model).
- Download the Ollama model automatically on first run.

## 3. Service Access

| Service      | URL                      | Notes                                |
|--------------|--------------------------|--------------------------------------|
| Frontend     | http://localhost:5173    | Main chat UI                         |
| Backend API  | http://localhost:8000    | FastAPI endpoints                    |
| ChromaDB     | http://localhost:8001    | Vector DB (internal, rarely needed) |
| Ollama       | http://localhost:11434   | LLM API (internal, rarely needed)   |

## 4. Data Persistence
- **Uploaded files**: `./data/files` (host volume)  
- **ChromaDB data**: `./data/chroma_db` (host volume)  
- **Ollama models**: Docker volume `ollama_models` (persistent between runs)

## 5. Environment Variables
Set sensitive values in a `.env` file at the project root:

```env
CHAT_RAG_ADMIN_TOKEN=your_admin_token_here
```

Used for admin endpoints and internal service configuration.

## 6. Updating Models or Services

To update the Ollama model:
- Change the entrypoint in `docker-compose.yml` to pull a different model/tag.

To upgrade a service:
- Pull the latest image or rebuild the relevant Dockerfile, then run:

```sh
docker compose up --build
```

## 7. Stopping and Cleaning Up

To stop all services:

```sh
docker compose down
```

To remove all containers, networks, and volumes:

```sh
docker compose down -v
```

## 8. Troubleshooting
- **Model download is slow**: The first run may take time as `mistral:latest` is downloaded.
- **Port conflicts**: Change the mapped ports in `docker-compose.yml` if needed.
- **File permissions**: Ensure your user can write to `./data/files` and `./data/chroma_db`.

## 9. Scalability & Upgradeability
- Each service is independent and can be updated or scaled in `docker-compose.yml`.
- For production, consider splitting frontend/backend hosting or using orchestration platforms (Kubernetes, ECS, etc).

## 10. References
- [Ollama Docs](https://ollama.com)
- [ChromaDB Docs](https://docs.trychroma.com)
- [Docker Compose Docs](https://docs.docker.com/compose)

For more details, see `gotchas.md` and `implementation_details.md`.

**If you change the architecture, always update this reference and log the change!**
```

Want me to generate a downloadable `.md` file for you?
