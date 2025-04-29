# Implementation Details

## LLM Integration Migration (Backend)

### ✅ Migration Complete & System Verified
- The backend now uses `langchain-ollama` (`OllamaLLM`) for all LLM operations, with global instantiation for efficiency.
- All legacy/deprecated imports have been removed.
- Requirements and code are fully in sync and tested.
- No errors encountered during chat or file operations after install and restart.
- Documentation and codebase are up to date as of 2025-04-29.
- **Rationale:** Ensures maintainability, future-proofs LLM integration, and provides a clear reference point for future upgrades.

- **Context:**
  - Migrated from deprecated `langchain.llms.Ollama` to `langchain-ollama.OllamaLLM` for future-proofing and to resolve deprecation warnings.
  - LLM is now instantiated globally at the top of `main.py` for efficiency.
  - Updated requirements: added `langchain-community` and `langchain-ollama` to `requirements.txt`.
- **Rationale:**
  - Ensures compatibility with LangChain v0.2.0+ and prepares for v1.0.0.
  - Reduces import overhead and improves maintainability.
- **Date:** 2025-04-29

---

## Frontend State Management & UX Fixes

### ✅ Source Display Improvement (Chat)
- Chat message sources now display clear file information (filename or source_file) instead of `[object Object]`.
- File updated: `frontend/src/components/Chat/ChatBubble.tsx`.
- **Rationale:** Improves user experience and clarity when referencing source documents for answers.
- **Date:** 2025-04-29

- **Zustand Import Update:**
  - Updated all Zustand store imports to use `import { create } from 'zustand'` instead of the deprecated default import.
  - Files updated: `frontend/src/state/filesStore.ts`, `frontend/src/state/chatStore.ts`.
  - **Rationale:** Prevents deprecation warnings and ensures future compatibility.

- **React setState Warning Fix:**
  - Moved toast error notification in `ChatInput.tsx` into a `useEffect` hook.
  - File updated: `frontend/src/components/Chat/ChatInput.tsx`.
  - **Rationale:** Prevents "Cannot update a component while rendering a different component" warning. Ensures toasts and state updates are not called during render.

- **Date:** 2025-04-29

---

## Gemini-Style Sticky Chat Input (Frontend)

- **Context:**
  - The chat input field is now always visible at the bottom of the chat area (sticky), following Gemini-style UX best practices.
  - This ensures users can send messages at any time without scrolling, improving accessibility and usability.
- **Implementation:**
  - Updated `frontend/src/components/Chat/ChatArea.tsx` to use Chakra UI's `Flex` and `Box` with `position="sticky"` for the input.
  - The chat messages area scrolls independently above the input.
- **Reference:**
  - See `ChatArea.tsx` for layout details.
- **Date:** 2025-04-29

---

## Chroma Vectorstore Persistence (LangChain)

- **Context:**
  - The `.persist()` method is no longer available on the `Chroma` object in recent versions of `langchain_chroma`.
  - Persistence is now handled automatically when a `persist_directory` is specified during `Chroma` instantiation.
- **Implementation:**
  - In `RAGPipeline.ingest`, all calls to `.persist()` have been removed.
  - A clarifying comment has been added in the code.
- **Reference:**
  - See `backend/app/rag/pipeline.py`, `RAGPipeline.ingest` method.
- **Date:** 2025-04-29

---

## API Routing Consistency

- All backend API endpoints now use the `/api/` prefix for seamless integration with the frontend Vite proxy and to avoid 404 errors.
- See `backend/app/main.py` for route definitions.
