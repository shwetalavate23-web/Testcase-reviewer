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
    model: str = os.getenv("MODEL", "gpt-4o-mini")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    timeout: int = int(os.getenv("TIMEOUT", "60"))
    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")


settings = Settings()
