import os
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
import logging
import asyncio
import google.generativeai as genai
import time
from tenacity import retry, stop_after_attempt, wait_exponential

"""
RAG pipeline using Google's Gemini models (free version) for both embeddings and chat
"""

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.csv', '.xlsx'}

class RAGPipeline:
    def __init__(self, vector_db_path: str = "./chroma_db", chunking_strategy: str = "auto", api_key: str = None):
        """
        :param vector_db_path: Path for ChromaDB persistence
        :param chunking_strategy: 'auto', 'header', or 'character'. If 'auto', use header-based for markdown, otherwise fallback.
        :param api_key: Google API key for Gemini models
        """
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        self.vector_db_path = vector_db_path
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = Chroma(persist_directory=self.vector_db_path, embedding_function=self.embeddings)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            convert_system_message_to_human=True,
            temperature=0.7,
            max_output_tokens=2048,
        )
        self.chunking_strategy = chunking_strategy
        logging.info(f"Initialized RAGPipeline with Gemini free tier models (chunking_strategy={chunking_strategy})")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _embed_with_retry(self, texts: List[str]) -> List[List[float]]:
        """Retry embedding with exponential backoff for rate limits"""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                logging.warning(f"Rate limit hit, retrying: {e}")
                raise  # Retry
            raise  # Don't retry other errors

    def _get_text_splitter(self, docs, file_path: str):
        """
        Use MarkdownHeaderTextSplitter if markdown, else fallback to RecursiveCharacterTextSplitter.
        """
        ext = os.path.splitext(file_path)[-1].lower()
        if self.chunking_strategy == "header" or (self.chunking_strategy == "auto" and ext in ['.md', '.markdown']):
            try:
                return MarkdownHeaderTextSplitter(headers_to_split_on=["#", "##", "###"], chunk_size=1000, chunk_overlap=100)
            except Exception as e:
                logging.warning(f"Header splitter failed: {e}, falling back to character splitter.")
        # Fallback
        return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

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
        """
        Ingests a file using adaptive chunking (header-based for markdown, otherwise character-based).
        """
        docs = self.load_document(file_path)
        splitter = self._get_text_splitter(docs, file_path)
        splits = splitter.split_documents(docs)
        # Attach file-level metadata
        for doc in splits:
            doc.metadata = doc.metadata or {}
            if metadata:
                doc.metadata.update(metadata)
            doc.metadata['source_file'] = file_path
        # Process in smaller batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(splits), batch_size):
            batch = splits[i:i + batch_size]
            try:
                self.vectorstore.add_documents(batch)
                time.sleep(1)  # Rate limit protection
            except Exception as e:
                logging.error(f"Failed to ingest batch {i}-{i+len(batch)}: {e}")
                raise
        logging.info(f"Ingested {len(splits)} chunks from {file_path} using {splitter.__class__.__name__}")

    def retrieve(self, query: str, k: int = 4, keywords: Optional[list] = None, metadata_filter: Optional[dict] = None) -> List[Document]:
        """
        Hybrid retrieval: combines vector search, keyword, and metadata filtering. Always uses strict top-k retrieval (no MMR).
        :param query: user query
        :param k: number of results
        :param keywords: list of keywords to boost/filter
        :param metadata_filter: dict of metadata filters (e.g. {"source_file": ...})
        """
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        if metadata_filter:
            results = retriever.invoke(query, filter=metadata_filter)
        else:
            results = retriever.invoke(query)
        # Keyword filter/boost
        if keywords:
            keyword_results = [doc for doc in results if any(kw.lower() in doc.page_content.lower() for kw in keywords)]
            # Merge, deduplicate, and sort (keyword hits first)
            unique = {id(doc): doc for doc in keyword_results + results}
            results = list(unique.values())[:k]
        logging.info(f"Hybrid retrieval for query '{query}': {len(results)} docs (strict top-k, keywords={keywords}, metadata={metadata_filter})")
        return results
