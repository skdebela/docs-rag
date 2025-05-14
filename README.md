# RAG Chat

A **privacy-focused Retrieval-Augmented Generation (RAG) chat app** powered by Google's Gemini models. Upload documents, ask questions, and get answers with sources—all while maintaining control over your data.

---

## Features

- **Gemini-Powered RAG Pipeline**: Uses Google's state-of-the-art Gemini models for both chat and embeddings.
- **File Upload & Parsing**: Supports DOCX, PDF, and more (via `unstructured`, `python-docx`, `pdfplumber`).
- **Modern UI**: Gemini-style, minimal, and accessible. Built with Vite, React, TypeScript, Zustand, Chakra UI.
- **Chat with Sources**: Ask questions and see which documents/sections the answer comes from.
- **FastAPI Backend**: Robust API, clean separation from frontend, `/api` route organization.
- **Extensible & Documented**: Modular, testable code with strict documentation and change management policies.

---

## Quick Start

### 1. **Requirements**
- Python 3.9+
- Node.js 18+
- Google Cloud API Key (for Gemini models)

---

## 🚀 Quick Setup Checklist

1. **Get a Google API Key** for Gemini models
2. **Set up backend** (Python, FastAPI)
3. **Set up frontend** (Node.js, Vite)
4. **Open the app** in your browser: [http://localhost:5173](http://localhost:5173)

---

### 2. Get Google API Key
- **Get API Key:** Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get your API key
- **Set Environment Variable:**
  ```bash
  export GOOGLE_API_KEY="your-api-key-here"
  ```
  > Make sure to keep your API key secure and never commit it to version control.

### 3. Backend Setup (FastAPI)
- **Create and activate a virtual environment:**
  ```bash
  cd backend
  python -m venv .venv
  source .venv/bin/activate
  ```
- **Install Python dependencies:**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```
- **Start the backend server:**
  ```bash
  uvicorn app.main:app --reload
  ```
  - The backend API will be available at: [http://localhost:8000/api](http://localhost:8000/api)

### 4. Frontend Setup (Vite)
- **Install Node.js dependencies:**
  ```bash
  cd frontend
  npm install
  ```
- **Start the frontend dev server:**
  ```bash
  npm run dev
  ```
  - The frontend app will be available at: [http://localhost:5173](http://localhost:5173)

---

## ✅ Quick Setup Checklist
- [ ] Google API key obtained and set as environment variable
- [ ] Backend running at [http://localhost:8000/api](http://localhost:8000/api)
- [ ] Frontend running at [http://localhost:5173](http://localhost:5173)

---

## How to Use the App
- Open [http://localhost:5173](http://localhost:5173) in your browser.
- Upload your files using the sidebar.
- Ask questions in the chat box; answers will cite document sources.
- All processing uses Google's Gemini models—your data is processed securely.

---

## Troubleshooting & Tips
- **API Key Issues:**
  - Make sure `GOOGLE_API_KEY` environment variable is set correctly.
  - Check that your API key has access to Gemini models.
- **Python dependency errors:**
  - Make sure your virtual environment is activated and `pip` is up to date.
- **Node/npm errors:**
  - Use Node.js 18+ and delete/reinstall `node_modules` if issues persist.
- **PDF/DOCX parsing errors:**
  - Install `libmagic` and `poppler-utils` (see backend gotchas).
- **For more help:**
  - See [`backend/gotchas.md`](backend/app/gotchas.md) and [`backend/implementation_details.md`](backend/app/implementation_details.md).

---

## Architecture

- **Frontend**: Vite + React + TypeScript + Zustand + Chakra UI
- **Backend**: FastAPI + SQLAlchemy + LangChain + ChromaDB + Unstructured
- **LLM & Embeddings**: Google's Gemini models via `langchain-google-genai`
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
- **Change Gemini Model:** Edit the model name in `backend/app/main.py` (`ChatGoogleGenerativeAI(model="gemini-pro")`).
- **Add File Types:** Extend file parsing in the backend pipeline.
- **UI/UX:** Tweak Chakra UI theme or component structure in `frontend/src/components`.

---

## Documentation & Policies
- All operational quirks, architecture decisions, and gotchas are logged in `backend/implementation_details.md`, `gotchas.md`, and `quick_reference.md`.
- Strict documentation and code quality policies are followed—see project docs for details.

---

## Credits
- Built by Tarek Adam Mustafa and contributors.
- Powered by: [Google Gemini](https://deepmind.google/technologies/gemini/), [LangChain](https://github.com/langchain-ai/langchain), [ChromaDB](https://www.trychroma.com/), [Unstructured](https://unstructured.io/), [Chakra UI](https://chakra-ui.com/), [Vite](https://vitejs.dev/).

---

## License
[MIT](LICENSE)
