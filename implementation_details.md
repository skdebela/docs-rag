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

### Chat Architecture (2025-04-29)
- **Async chat flow**: Zustand store exposes async `sendChat`, which sends user message to backend and only updates messages after backend response (AI answer and sources).
- **Loading/Error state**: Store tracks loading and error, UI disables input and shows spinner while waiting, and displays errors via toast/alert.
- **Backend sync**: No local-only chat updates; all state changes reflect backend truth.
- **Gemini-style UI/UX**: Minimal, accessible, with clear separation between chat and file controls.
- **Rationale**: Ensures robust, user-friendly experience, prevents UI/backend drift, and supports future backend evolution.

## References
- Context7 Langchain docs (April 2025): RAG pipeline, loaders, ChromaDB, Ollama embeddings.

## Next Steps
- Integrate this pipeline into API endpoints for file upload and chat.
- Log all operational events and edge cases in `gotchas.md` as encountered.
