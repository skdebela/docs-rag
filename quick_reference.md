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
