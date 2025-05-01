"""
Modular, production-ready RAG pipeline for LangChain + ChromaDB + Ollama
- No NLTK or external data dependencies
- Advanced retrieval (vector search, metadata filtering, top-k)
- Metadata-rich chunking
- Prompt engineering (system prompt, context, user question)
- Async and streaming ready
- Comprehensive logging
"""
import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.documents import Document
import logging
import asyncio

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv', '.xlsx'}

class ModularRAGPipeline:
    def __init__(self, vector_db_path: str = "./chroma_db"):
        self.vector_db_path = vector_db_path
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self.vectorstore = Chroma(persist_directory=self.vector_db_path, embedding_function=self.embeddings)
        self.llm = OllamaLLM(model="llama3")  # Change model as needed
        logging.info("Initialized ModularRAGPipeline with ChromaDB and Ollama.")

    def load_document(self, file_path: str) -> List[Document]:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
        elif ext == '.docx':
            loader = UnstructuredWordDocumentLoader(file_path)
        elif ext == '.txt':
            loader = TextLoader(file_path)
        elif ext == '.csv':
            loader = CSVLoader(file_path)
        elif ext == '.xlsx':
            loader = UnstructuredExcelLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        docs = loader.load()
        return docs

    def ingest(self, file_path: str, metadata: Optional[dict] = None):
        docs = self.load_document(file_path)
        # Chunk and attach metadata
        splits = self.text_splitter.split_documents(docs)
        for doc in splits:
            doc.metadata = doc.metadata or {}
            if metadata:
                doc.metadata.update(metadata)
            doc.metadata['source_file'] = file_path
        self.vectorstore.add_documents(splits)
        logging.info(f"Ingested {len(splits)} chunks from {file_path}")

    def retrieve(self, query: str, k: int = 4, metadata_filter: Optional[dict] = None) -> List[Document]:
        # Top-k vector search with optional metadata filtering
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        if metadata_filter:
            results = retriever.invoke(query, filter=metadata_filter)
        else:
            results = retriever.invoke(query)
        logging.info(f"Retrieved {len(results)} docs for query: {query}")
        return results

    def build_prompt(self, context: List[Document], question: str) -> str:
        context_text = "\n---\n".join([doc.page_content for doc in context])
        prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.\nContext:\n{context_text}\n---\nUser question: {question}"""
        return prompt

    async def generate(self, prompt: str) -> str:
        # Async call to Ollama (if supported)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.llm.invoke, prompt)
        logging.info("Generated answer from LLM.")
        return result

    def chat(self, question: str, k: int = 4, metadata_filter: Optional[dict] = None) -> Dict[str, Any]:
        """Sync chat endpoint for compatibility."""
        context = self.retrieve(question, k=k, metadata_filter=metadata_filter)
        prompt = self.build_prompt(context, question)
        answer = self.llm.invoke(prompt)
        # Log retrieval and answer
        logging.info({
            "question": question,
            "retrieved_docs": [doc.metadata for doc in context],
            "answer": answer[:200] + ("..." if len(answer) > 200 else "")
        })
        return {"answer": answer, "sources": [doc.metadata for doc in context]}

    async def chat_async(self, question: str, k: int = 4, metadata_filter: Optional[dict] = None) -> Dict[str, Any]:
        context = self.retrieve(question, k=k, metadata_filter=metadata_filter)
        prompt = self.build_prompt(context, question)
        answer = await self.generate(prompt)
        logging.info({
            "question": question,
            "retrieved_docs": [doc.metadata for doc in context],
            "answer": answer[:200] + ("..." if len(answer) > 200 else "")
        })
        return {"answer": answer, "sources": [doc.metadata for doc in context]}

# Usage example (for docs):
# pipeline = ModularRAGPipeline()
# pipeline.ingest("/path/to/file.pdf", metadata={"uploaded_by": "user1"})
# result = pipeline.chat("What are the main findings?", k=6)
# print(result["answer"])
