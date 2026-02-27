"""Embedding model factory for RAG."""

from __future__ import annotations

import os

from langchain_openai import OpenAIEmbeddings

from app.config import settings


def get_embedding_model() -> OpenAIEmbeddings:
    """Return OpenAI embedding model configured from environment."""
    api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to initialize embedding model")

    return OpenAIEmbeddings(model=settings.embedding_model, api_key=api_key)
