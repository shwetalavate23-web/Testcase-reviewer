"""Text chunking helpers for RAG indexing."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping character chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks
