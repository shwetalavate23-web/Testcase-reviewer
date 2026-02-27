"""Retriever orchestration for guideline RAG context."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_chroma import Chroma

from app.config import settings
from app.rag.chunker import chunk_text
from app.rag.embeddings import get_embedding_model
from app.rag.loader import load_guideline
from app.rag.vectorstore import build_vector_store, load_vector_store


@dataclass(slots=True)
class GuidelineRetriever:
    """Thin wrapper around vector store retrieval."""

    store: Chroma

    def retrieve_context(self, query: str, k: int) -> list[str]:
        docs = self.store.similarity_search(query=query, k=k)
        return [doc.page_content for doc in docs if doc.page_content.strip()]


def initialize_retriever() -> GuidelineRetriever:
    """Initialize retriever by loading/building the persistent vector store."""
    guideline_text = load_guideline(settings.guideline_doc_path)
    chunks = chunk_text(guideline_text, settings.chunk_size, settings.chunk_overlap)
    embedding_model = get_embedding_model()

    try:
        store = load_vector_store(settings.vector_db_path, embedding_model)
    except FileNotFoundError:
        store = build_vector_store(chunks, settings.vector_db_path, embedding_model)

    return GuidelineRetriever(store=store)
