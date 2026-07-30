"""
ai/ollama_client.py — Low-level HTTP client for the Ollama REST API.
Shared by all model implementations; handles retries, timeouts,
and TTL-cached model availability to avoid repeated /api/tags calls.
"""
from __future__ import annotations

import json
import threading
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT, LLM_HEALTH_CHECK_TIMEOUT
from utils.logger import get_logger

log = get_logger(__name__)

_MODEL_CACHE_TTL = 30  # seconds between /api/tags refreshes


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    adapter = HTTPAdapter(
        pool_connections=2,
        pool_maxsize=8,
        max_retries=Retry(total=1, backoff_factor=0.2, status_forcelist=[502, 503, 504]),
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class OllamaClient:
    """Thin wrapper around the Ollama /api/chat and /api/tags endpoints."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self._session = _make_session()
        self._models_cache: List[str] = []
        self._cache_ts: float = 0.0
        self._cache_lock = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────────
    def list_models(self, force: bool = False) -> List[str]:
        """Return names of locally available models (TTL-cached)."""
        now = time.monotonic()
        with self._cache_lock:
            if not force and (now - self._cache_ts) < _MODEL_CACHE_TTL:
                return self._models_cache
        try:
            resp = self._session.get(
                f"{self.base_url}/api/tags", timeout=LLM_HEALTH_CHECK_TIMEOUT
            )
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            with self._cache_lock:
                self._models_cache = models
                self._cache_ts = time.monotonic()
            return models
        except Exception as exc:
            log.warning("Could not list Ollama models: %s", exc)
            return self._models_cache  # return stale cache on failure

    def is_model_available(self, model: str) -> bool:
        """Check if a specific model is pulled and ready (uses cache)."""
        return any(model in name for name in self.list_models())

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Call /api/chat. Returns the full parsed JSON response dict.
        Raises requests.RequestException on network failure.
        """
        payload = {
            "model":    model,
            "messages": messages,
            "stream":   stream,
            "options":  {"temperature": temperature, "num_predict": max_tokens},
        }
        resp = self._session.post(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload),
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()

    def ping(self) -> bool:
        """Return True if Ollama server is reachable."""
        try:
            self._session.get(
                f"{self.base_url}/api/tags", timeout=LLM_HEALTH_CHECK_TIMEOUT
            )
            return True
        except Exception:
            return False


# ── Module-level singleton shared by all model implementations ────────────────
_shared_client: Optional[OllamaClient] = None
_client_lock = threading.Lock()


def get_client() -> OllamaClient:
    """Return the shared OllamaClient singleton."""
    global _shared_client
    if _shared_client is None:
        with _client_lock:
            if _shared_client is None:
                _shared_client = OllamaClient()
    return _shared_client
