"""LLM provider adapters with graceful fallback."""

from __future__ import annotations

import json
from urllib import request

from app.config import settings


class LLMClient:
    def generate(self, prompt: str) -> str:
        if settings.provider == "openai" and settings.openai_api_key:
            return self._openai(prompt)
        if settings.provider == "google" and settings.google_api_key:
            return self._google(prompt)
        if settings.provider == "ollama":
            return self._ollama(prompt)
        return ""

    def _post_json(self, url: str, payload: dict, headers: dict[str, str]) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method="POST")
        with request.urlopen(req, timeout=settings.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _openai(self, prompt: str) -> str:
        payload = {
            "model": settings.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }
        result = self._post_json(
            "https://api.openai.com/v1/chat/completions",
            payload,
            {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
        )
        return result["choices"][0]["message"]["content"]

    def _google(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.model}:generateContent"
            f"?key={settings.google_api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        result = self._post_json(url, payload, {"Content-Type": "application/json"})
        return result["candidates"][0]["content"]["parts"][0]["text"]

    def _ollama(self, prompt: str) -> str:
        result = self._post_json(
            f"{settings.ollama_host}/api/generate",
            {"model": settings.model, "prompt": prompt, "stream": False},
            {"Content-Type": "application/json"},
        )
        return result.get("response", "")
