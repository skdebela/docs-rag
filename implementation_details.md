# Implementation Details: RAG Pipeline (Local-First)

## Supported File Types
- PDF (`.pdf`): via `PyPDFLoader`
- Word (`.docx`): via `UnstructuredWordDocumentLoader`
- Text (`.txt`): via `TextLoader`
- CSV (`.csv`): via `CSVLoader`
- Excel (`.xlsx`): via `UnstructuredExcelLoader`

## Pipeline Steps
1. **File Parsing**: Loader selected by extension. Handles edge cases for CSV/XLSX (see Gotchas).
2. **Chunking**: `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=100).
3. **Embedding**: Uses Ollama model (`nomic-embed-text`) or `sentence-transformers`.
4. **Vector Storage**: ChromaDB (local, disk-based).
5. **Retrieval**: Vector search with top-k relevant chunks.

## CSV/XLSX Integration Quirks
- CSV: Each row is treated as a document chunk. Large CSVs may need custom chunking for context.
- XLSX: Loader extracts all sheet content as text. Complex formatting or formulas may not be preserved. For multi-sheet logic or custom parsing, extend the loader.

## Frontend Architecture

### File Management (2025-04-29)
- **Zustand store is always backend-synced**: All file operations (upload, delete, fetch) update Zustand state only after backend confirmation, preventing UI/backend drift.
- **FileMeta shape matches backend**: All file components and state use the backend's file model (`id:number, filename:string, upload_time:string, metadata:any`).
- **Upload/Delete logic**: File uploads and deletions are performed via API calls, with UI state updated only on success. This ensures robust, reliable user experience.
- **Error/Loading State**: All file actions show Chakra UI spinners, alerts, and toasts for real-time user feedback and accessibility.
- **Gemini-style UI/UX**: Clean, minimal, and accessible design with clear separation between chat and file controls, as per project requirements.
- **Rationale**: These patterns prevent state desync, provide clear user feedback, and ensure maintainability as backend evolves.

### Chat Context and File Deletion Policy (2025-04-29)

#### App Reset & Sync Policy (2025-04-29)
- **Admin Reset:** The backend exposes `/api/admin/clear_all` (token-protected) to delete all files and chat history from the DB and vectorstore. The frontend provides an AdminPanel with a reset button for safe access.
- **DB is Source of Truth:** The files table in the DB is always authoritative. The vectorstore must be kept in sync with the DB. All file and chat deletions update both DB and vectorstore, with `persist()` and vectorstore reload for Chroma.
- **Reset Flow:** On reset, DB and vectorstore are both wiped, and the UI is refreshed. This guarantees a fresh, in-sync state for uploads and chat.
- **Rationale:** Prevents desync bugs where deleted files linger in chat results. See gotchas.md for historical issues.


#### ChromaDB/LangChain Deletion Gotcha (2025-04-29)
- **Problem:** Deleted files may still be referenced in RAG results even after calling vectorstore.delete().
- **Root Causes:**
    - Not calling `persist()` after deletion (Chroma keeps changes in memory until persisted).
    - Not reloading/reinitializing the vectorstore after deletion (in-memory cache may still contain deleted docs).
    - Metadata mismatch or improper indexing.
- **Patch/Best Practice:**
    - After any vectorstore deletion, always call `persist()` to write changes to disk.
    - Immediately reinitialize the vectorstore object to clear any in-memory cache.
    - Always index metadata fields (like file_id, filename) used for deletion.
    - See: [LangChain Chroma deletion issue #4519](https://github.com/langchain-ai/langchain/issues/4519), [Chroma vectorstore deletion discussion](https://github.com/langchain-ai/langchain/discussions/9495)
- **Status:**
    - This patch is now implemented in `main.py`—deleted files are fully removed from both DB and vectorstore, and will not appear in future chat results.


- The chat context always includes **all files currently loaded in the sidebar** (i.e., all files present in the DB and not deleted).
- When a file is deleted from the sidebar:
    - All references to it in the database and vectorstore must be fully removed.
    - It must never appear in chat results or sources after deletion.
- This is the default and intended behavior for the RAG pipeline and chat UX.

### Chat Architecture (2025-04-29)
- **Async chat flow**: Zustand store exposes async `sendChat`, which sends user message to backend and only updates messages after backend response (AI answer and sources).
- **Loading/Error state**: Store tracks loading and error, UI disables input and shows spinner while waiting, and displays errors via toast/alert.
- **Backend sync**: No local-only chat updates; all state changes reflect backend truth.
- **Gemini-style UI/UX**: Minimal, accessible, with clear separation between chat and file controls.
- **Rationale**: Ensures robust, user-friendly experience, prevents UI/backend drift, and supports future backend evolution.

## RAG Pipeline Consolidation (2025-05-02)
- Removed `app/rag/pipeline_modular.py` and the `ModularRAGPipeline` class.
- Only `RAGPipeline` (in `app/rag/pipeline.py`) is used by the backend and referenced in `main.py`.
- Rationale: Avoid code duplication, reduce maintenance overhead, and ensure a single source of truth for RAG logic.
- All ingestion, retrieval, and LLM logic is now in `RAGPipeline`.

_Last updated: 2025-05-02 22:38:49+02:00_

## References
- Context7 Langchain docs (April 2025): RAG pipeline, loaders, ChromaDB, Ollama embeddings.

## Next Steps
- Integrate this pipeline into API endpoints for file upload and chat.
- Log all operational events and edge cases in `gotchas.md` as encountered.
