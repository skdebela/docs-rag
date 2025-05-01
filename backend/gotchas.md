# Gotchas & Integration Quirks

## [2025-05-01] Modular RAG Upgrade: No NLTK, Advanced Retrieval
- The pipeline is now fully modular: ingestion, retrieval, prompt, and LLM are separated for maintainability.
- No NLTK or external dependencies for chunking—only `RecursiveCharacterTextSplitter`.
- Supports advanced retrieval (top-k, metadata filtering), rich metadata, async, and logging.
- Ready for production and future enhancements.
- Symptom: Ingestion fails with error about missing 'punkt' resource.
- Root Cause: NLTK 'punkt' tokenizer data was not present in the environment.
- Fix: Code now auto-downloads 'punkt' if missing before ingestion. For robust, repeatable setup, always run:
  ```bash
  uv python -c "import nltk; nltk.download('punkt')"
  ```
  after installing dependencies. This ensures 'punkt' is present for all users and environments.
- Always ensure your virtual environment is activated when running this command, or use uv as shown above.

## Chroma Vectorstore `.persist()` Method Removed

- **Issue:**
  - The `.persist()` method is no longer available on the `Chroma` object in recent versions of `langchain_chroma`.
  - Attempting to call `.persist()` will raise an `AttributeError`.
- **Resolution:**
  - Persistence is now automatic when you specify a `persist_directory` during `Chroma` instantiation.
  - All calls to `.persist()` have been removed from the codebase.
- **Reference:**
  - See `RAGPipeline.ingest` in `backend/app/rag/pipeline.py` for the updated implementation and comment.

---

<!-- Log DB persistence gotcha here -->
---

## Action Items
- Always check for breaking changes in LangChain and Chroma APIs after upgrades.
- Document any future vectorstore persistence quirks here.

## Hybrid Retrieval API
- `/api/chat` now supports:
    - `keywords`: List of keywords to boost or filter retrieval.
    - `metadata_filter`: Dict for structured filtering (e.g. by file_id, section).
    - `use_mmr`: Use Maximal Marginal Relevance for re-ranking (default: True).
    - `k`: Number of chunks to retrieve (default: 4).
- Backwards compatible: legacy clients using only `question`/`file_id` query params still work.
- If both `file_id` and `metadata_filter` are provided, `file_id` is merged into metadata filter.
- Edge case: If no files are present, returns a friendly error.
- Always validate that returned sources match current DB files (prevents orphaned results).
