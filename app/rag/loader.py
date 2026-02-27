"""Guideline document loading utilities."""

from __future__ import annotations

from pathlib import Path


def load_guideline(path: str) -> str:
    """Load guideline text from a .md/.txt file path."""
    guideline_path = Path(path)
    if not guideline_path.exists():
        raise FileNotFoundError(f"Guideline file not found: {guideline_path}")
    if not guideline_path.is_file():
        raise ValueError(f"Guideline path is not a file: {guideline_path}")

    suffix = guideline_path.suffix.lower()
    if suffix not in {".md", ".txt"}:
        raise ValueError(f"Unsupported guideline format '{suffix}'. Use .md or .txt")

    content = guideline_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Guideline file is empty: {guideline_path}")
    return content
