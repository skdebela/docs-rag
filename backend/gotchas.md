# Gotchas & Integration Quirks

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

## Action Items
- Always check for breaking changes in LangChain and Chroma APIs after upgrades.
- Document any future vectorstore persistence quirks here.
