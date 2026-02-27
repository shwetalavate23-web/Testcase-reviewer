"""Configuration management for the testcase reviewer app."""

from dataclasses import dataclass
import os
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


@dataclass(slots=True)
class Settings:
    provider: str = os.getenv("PROVIDER", "openai")
    model: str = os.getenv("MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    llm_model: str = os.getenv("LLM_MODEL", os.getenv("MODEL", "gpt-4o-mini"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    timeout: int = int(os.getenv("TIMEOUT", "60"))
    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")
    guideline_doc_path: str = os.getenv("GUIDELINE_DOC_PATH", "app/rag/guidelines.md")
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", ".chroma/qa_guidelines")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    retrieval_k: int = int(os.getenv("RETRIEVAL_K", "4"))


settings = Settings()
