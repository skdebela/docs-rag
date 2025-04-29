# Local Chat RAG

A **local, privacy-first Retrieval-Augmented Generation (RAG) chat app**. Upload documents, ask questions, and get answers with sources—powered by open-source LLMs running on your own machine.

---

## Features

- **Local RAG Pipeline**: No cloud, no data leaks—everything runs on your machine.
- **File Upload & Parsing**: Supports DOCX, PDF, and more (via `unstructured`, `python-docx`, `pdfplumber`).
- **Modern UI**: Gemini-style, minimal, and accessible. Built with Vite, React, TypeScript, Zustand, Chakra UI.
- **Chat with Sources**: Ask questions and see which documents/sections the answer comes from.
- **FastAPI Backend**: Robust API, clean separation from frontend, `/api` route organization.
- **Ollama LLM Integration**: Use open-source models (Mistral, Llama2, etc.) locally via Ollama.
- **Extensible & Documented**: Modular, testable code with strict documentation and change management policies.

---

## Quick Start

### 1. **Requirements**
- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.com/) (for LLMs)

### 2. **Setup**

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

#### LLM Model (Ollama)
Ensure [Ollama](https://ollama.com/) is installed and running.
```bash
ollama pull mistral  # or llama2, phi3, etc.
ollama serve
```

### 3. **Run the App**

#### Backend (FastAPI)
```bash
cd backend
uvicorn app.main:app --reload
```

#### Frontend (Vite)
```bash
cd frontend
npm run dev
```

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000/api](http://localhost:8000/api)

---

## Usage
- **Upload files** in the sidebar.
- **Ask questions** in the chat—answers are generated using your documents as context.
- **Sources** are shown for every answer (deduplicated by file).
- **All processing is local**—your data never leaves your device.

---

## Architecture

- **Frontend**: Vite + React + TypeScript + Zustand + Chakra UI
- **Backend**: FastAPI + SQLAlchemy + LangChain + ChromaDB + Unstructured
- **LLM**: Ollama (Mistral, Llama2, etc.) via `langchain-ollama`
- **RAG Pipeline**: Chunking, embedding, retrieval, and chat with sources

### Folder Structure
```
ChatRAG/
  backend/
    app/
      main.py           # FastAPI app & API endpoints
      db/               # Database models & session
      rag/              # RAG pipeline logic
    requirements.txt
    ...
  frontend/
    src/
      components/       # UI components (Chat, Files, Layout)
      state/            # Zustand stores
      ...
    vite.config.ts
    ...
```

---

## Customization
- **Change LLM Model:** Edit the model name in `backend/app/main.py` (`OllamaLLM(model="mistral")`).
- **Add File Types:** Extend file parsing in the backend pipeline.
- **UI/UX:** Tweak Chakra UI theme or component structure in `frontend/src/components`.

---

## Documentation & Policies
- All operational quirks, architecture decisions, and gotchas are logged in `backend/implementation_details.md`, `gotchas.md`, and `quick_reference.md`.
- Strict documentation and code quality policies are followed—see project docs for details.

---

## Troubleshooting
- **Ollama not running:** Start it with `ollama serve` and ensure your model is pulled.
- **500 errors on chat:** Check backend logs for missing models or misconfigurations.
- **Sources show `[object Object]`:** This is fixed—sources are now deduplicated and display filenames.

---

## Credits
- Built by Tarek Adam Mustafa and contributors.
- Powered by open-source: [Ollama](https://ollama.com/), [LangChain](https://github.com/langchain-ai/langchain), [ChromaDB](https://www.trychroma.com/), [Unstructured](https://unstructured.io/), [Chakra UI](https://chakra-ui.com/), [Vite](https://vitejs.dev/).

---

## License
[MIT](LICENSE)
