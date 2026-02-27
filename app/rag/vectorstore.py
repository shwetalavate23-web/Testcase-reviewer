"""Persistent vector store operations for guideline chunks."""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


COLLECTION_NAME = "qa_guidelines"


def _has_existing_store(persist_dir: str) -> bool:
    path = Path(persist_dir)
    if not path.exists():
        return False
    return any(path.iterdir())


def build_vector_store(chunks: list[str], persist_dir: str, embedding_model: OpenAIEmbeddings) -> Chroma:
    """Build and persist a Chroma vector store from text chunks."""
    if not chunks:
        raise ValueError("Cannot build vector store with no chunks")

    documents = [Document(page_content=chunk, metadata={"source": "guidelines"}) for chunk in chunks]
    store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_dir,
        collection_name=COLLECTION_NAME,
    )
    return store


def load_vector_store(persist_dir: str, embedding_model: OpenAIEmbeddings) -> Chroma:
    """Load existing persistent Chroma vector store."""
    if not _has_existing_store(persist_dir):
        raise FileNotFoundError(f"Vector DB not found at: {persist_dir}")

    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_model,
        collection_name=COLLECTION_NAME,
    )
