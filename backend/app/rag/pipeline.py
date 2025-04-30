import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain_text_splitters import NLTKTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv', '.xlsx'}

class RAGPipeline:
    def __init__(self, vector_db_path: str = "./chroma_db"):
        self.vector_db_path = vector_db_path
                # Prefer semantic chunking using NLTKTextSplitter (sentence-aware)
        try:
            self.text_splitter = NLTKTextSplitter(chunk_size=1000, chunk_overlap=100)
        except Exception as e:
            # Fallback to RecursiveCharacterTextSplitter if NLTK not installed
            print("Warning: NLTK not available, falling back to character-based chunking. Error:", e)
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")  # or sentence-transformers
        self.vectorstore = Chroma(persist_directory=self.vector_db_path, embedding_function=self.embeddings)

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

    def ingest(self, file_path: str, metadata: dict = None):
        docs = self.load_document(file_path)
        splits = self.text_splitter.split_documents(docs)
        # Attach file-level metadata
        for doc in splits:
            doc.metadata = doc.metadata or {}
            if metadata:
                doc.metadata.update(metadata)
            doc.metadata['source_file'] = file_path
        self.vectorstore.add_documents(splits)
        # Persistence is automatic in langchain_chroma when using persist_directory.

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)
