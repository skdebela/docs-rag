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

_Last updated: 2025-04-29_
