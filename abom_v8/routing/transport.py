"""Model transports.  Ollama is one execution substrate, not the architecture.

Transports only move a prompt to a model and return text.  Placement and routing
never inspect them.  Standard library only; no request is made at import time.
"""
from __future__ import annotations

import json
from typing import Protocol
from urllib import error, parse, request

DEFAULT_OLLAMA_URL = "http://localhost:11434"


class TransportError(RuntimeError):
    """The transport could not complete the request."""


class Transport(Protocol):
    transport_id: str

    def generate(self, model_id: str, prompt: str, *, timeout: float = 60.0) -> str: ...


class OllamaTransport:
    """Non-streaming client for a local Ollama server."""

    transport_id = "ollama"

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL) -> None:
        parts = parse.urlsplit(base_url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("base_url must be an http(s) URL")
        self.base_url = base_url.rstrip("/")

    def _call(self, path: str, payload: dict | None, timeout: float) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url + path, data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if payload is None else "POST",
        )
        try:
            with request.urlopen(req, timeout=timeout) as response:  # noqa: S310 (scheme checked)
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, OSError, ValueError) as exc:
            raise TransportError(f"ollama request to {path} failed: {exc}") from exc
        if not isinstance(body, dict):
            raise TransportError(f"unexpected ollama response from {path}")
        return body

    def generate(self, model_id: str, prompt: str, *, timeout: float = 60.0) -> str:
        body = self._call("/api/generate",
                          {"model": model_id, "prompt": prompt, "stream": False}, timeout)
        text = body.get("response")
        if not isinstance(text, str):
            raise TransportError("ollama response had no text")
        return text

    def list_models(self, *, timeout: float = 10.0) -> tuple[str, ...]:
        """Installed model names, for finding models that are not yet placed."""
        body = self._call("/api/tags", None, timeout)
        models = body.get("models", [])
        names = [m.get("name") for m in models if isinstance(m, dict)]
        return tuple(n for n in names if isinstance(n, str))
