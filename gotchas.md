# Gotchas & Integration Quirks

## Frontend File Management (2025-04-29)
- Zustand file state must be backend-synced; local-only updates cause UI drift.
- FileMeta shape/type must match backend (`id:number, filename:string` etc.); type mismatches break UI.
- File upload and deletion update state only after backend confirms success.
- All file actions (upload, fetch, delete) show loading and error feedback via Chakra UI toasts/alerts.
- All known quirks resolved; future backend changes may require frontend refactor.

## Chat Integration (2025-04-29)
- Chat flow is fully async: user messages are sent to backend, AI responses are only shown after backend returns.
- Zustand chat state tracks loading and error; UI disables input and shows spinner during backend call.
- Error states are shown via Chakra UI toast and alert; ensures user always has feedback.
- Gemini-style UI/UX: chat and file controls remain clearly separated, minimal, and accessible.
- If backend response shape changes, frontend must be updated accordingly.

## File Type Quirks
- **CSV**: Each row is treated as a document. Large CSVs may result in many small chunks—consider custom chunking for very wide/long tables.
- **XLSX**: Loader extracts all sheet content as text. Complex formatting, formulas, or multi-sheet logic may not be preserved. For advanced use, extend or customize the loader.

## Integration Issues
- All vectorization and LLM inference are local, but hardware resource usage (RAM/CPU) can spike with large files or concurrent uploads/queries.
- If Ollama or ChromaDB is not running or misconfigured, ingestion and chat endpoints will fail. Ensure all local services are started before use.

## Deletion Hygiene
- Deleting a file removes it from the DB, disk, and vector store. If deletion fails at any step, partial cleanup may be required.

## Error Handling
- All API endpoints return clear error messages for unsupported file types, ingestion errors, or LLM failures.
- Chat endpoint will return 500 if LLM inference fails (e.g., Ollama not available).

## Security
- No authentication by default. For multi-user or sensitive deployments, add user auth and HTTPS.

---

## Backend SQLAlchemy Reserved Name Pitfall (2025-04-29)
- **Issue:** Using `metadata` as a model attribute in SQLAlchemy Declarative models causes `InvalidRequestError` because `metadata` is reserved for SQLAlchemy's internal use.
- **Fix:** Renamed all `metadata` usages in the `File` model (and all references) to `file_metadata`.
- **Lesson:** Avoid using `metadata` as a column/attribute name in SQLAlchemy models.
- **Reference:** See [SQLAlchemy docs](https://docs.sqlalchemy.org/en/20/orm/metadata.html#metadata)


## Backend Migration: OllamaEmbeddings to langchain_ollama (2025-04-29)
- **Issue:** LangChain deprecated OllamaEmbeddings in the main/langchain_community packages. Import must now come from `langchain_ollama`.
- **Fix:** Updated all imports and usages in `app/rag/pipeline.py` to use `from langchain_ollama import OllamaEmbeddings`.
- **Lesson:** Monitor LangChain release notes for breaking changes and migration requirements.
- **Reference:** See [LangChain v0.2 migration docs](https://python.langchain.com/docs/versions/v0_2/)

[2025-04-29T14:57:56+02:00] **Solution Update:** Added /api/admin/clear_all endpoint and AdminPanel UI for full app reset. This deletes all files and chat history from both DB and vectorstore, guarantees a fresh start, and keeps all layers in sync. DB is always the source of truth; vectorstore is wiped and reloaded to match. Use this if you ever suspect a desync or want a clean slate.

## Dead Code Removal (2025-05-02)
- Deleted `backend/app/rag/pipeline_modular.py` (ModularRAGPipeline) as it was not referenced anywhere in production code.
- Only `RAGPipeline` is used in backend entrypoint and services.
- If ModularRAGPipeline is needed in the future, restore from version control and refactor as a utility.

[2025-05-02T22:38:49+02:00] **Persistent Gotcha:** Deleted files still referenced in RAG/chat after deletion
- **Symptom:** Chat answers reference files that were deleted from the sidebar and database.
- **Root Cause:** ChromaDB/LangChain vectorstore does not fully remove embeddings unless `persist()` is called and the vectorstore is reloaded. In-memory cache or on-disk state may get out of sync.
- **Solution:** After any vectorstore deletion, always call `persist()` and reinitialize the vectorstore object. See implementation in `main.py`.
- **References:** [LangChain Chroma deletion issue #4519](https://github.com/langchain-ai/langchain/issues/4519), [Chroma vectorstore deletion discussion](https://github.com/langchain-ai/langchain/discussions/9495)
[2025-04-30T22:20:31.917450] [init_db] Database initialized successfully.
[2025-04-30T22:46:27.683850] [init_db] Database initialized successfully.
[2025-04-30T23:07:41.281882] [init_db] Database initialized successfully.
[2025-04-30T23:25:50.709204] [init_db] Database initialized successfully.
[2025-04-30T23:27:20.038590] [init_db] Database initialized successfully.
[2025-04-30T23:28:03.099300] [DeleteFile] File 1 deleted successfully at 2025-04-30T23:28:03.099273
[2025-05-01T20:46:42.481981] [init_db] Database initialized successfully.
[2025-05-01T21:15:11.799796] [init_db] Database initialized successfully.
[2025-05-01T21:21:34.707522] [init_db] Database initialized successfully.
[2025-05-01T21:46:26.162927] [init_db] Database initialized successfully.
[2025-05-01T22:08:35.208184] [init_db] Database initialized successfully.
[2025-05-01T22:14:28.859316] [init_db] Database initialized successfully.
[2025-05-01T22:20:56.845546] [init_db] Database initialized successfully.
[2025-05-01T22:22:06.407261] [init_db] Database initialized successfully.
[2025-05-01T22:22:07.378095] [init_db] Database initialized successfully.
[2025-05-01T22:26:31.518365] [init_db] Database initialized successfully.
[2025-05-01T22:31:51.311059] [init_db] Database initialized successfully.
[2025-05-01T22:33:24.218829] [init_db] Database initialized successfully.
[2025-05-01T22:33:48.691504] [init_db] Database initialized successfully.
[2025-05-01T22:45:07.108418] [init_db] Database initialized successfully.
[2025-05-01T22:46:04.115501] [init_db] Database initialized successfully.
[2025-05-01T22:46:09.440543] [init_db] Database initialized successfully.
[2025-05-01T22:48:56.625709] [init_db] Database initialized successfully.
[2025-05-01T22:50:20.623153] [init_db] Database initialized successfully.
[2025-05-01T22:51:05.591741] [init_db] Database initialized successfully.
[2025-05-01T22:54:11.358273] [init_db] Database initialized successfully.
[2025-05-01T22:56:35.032317] [init_db] Database initialized successfully.
[2025-05-01T22:58:05.335563] [init_db] Database initialized successfully.
[2025-05-01T23:01:32.799624] [init_db] Database initialized successfully.
[2025-05-01T23:03:19.232019] [init_db] Database initialized successfully.
[2025-05-02T12:31:35.886484] [init_db] Database initialized successfully.
[2025-05-02T12:37:55.884577] [init_db] Database initialized successfully.
[2025-05-02T12:41:49.232525] [init_db] Database initialized successfully.
[2025-05-02T16:02:48.456745] [init_db] Database initialized successfully.
[2025-05-02T22:41:39.354171] [init_db] Database initialized successfully.
