"""
ai/llm_router.py — Auto-switching LLM router with non-blocking health checks.
Availability check runs in a background thread so startup is never blocked.
"""
from __future__ import annotations

import threading
from typing import List, Optional

from ai.base_llm import BaseLLM, LLMMessage, LLMResponse
from ai.model_implementations import DeepSeekModel, LlamaModel, QwenModel
from ai.ollama_client import get_client
from utils.logger import get_logger

log = get_logger(__name__)

_RULE_BASED_FALLBACK = (
    "I'm sorry, the AI service is currently unavailable. "
    "Please ensure Ollama is running and at least one model is pulled. "
    "Run: ollama pull qwen3"
)


class LLMRouter:
    """
    Ordered list of LLM backends with automatic fallback.
    Availability check is deferred to a background thread — __init__ returns
    immediately so application startup is not blocked by network I/O.
    """

    def __init__(self) -> None:
        self._models: List[BaseLLM] = [QwenModel(), DeepSeekModel(), LlamaModel()]
        self._active_index: int = 0
        self._ready = threading.Event()
        # Run health check off the main thread
        threading.Thread(target=self._check_availability, daemon=True).start()

    def _check_availability(self) -> None:
        client = get_client()
        if not client.ping():
            log.warning("Ollama server not reachable at startup.")
            self._ready.set()
            return
        for i, model in enumerate(self._models):
            if model.is_available():
                self._active_index = i
                log.info("LLM Router: primary model set to %s", model.model_name)
                break
        else:
            log.warning("No Ollama models available. Rule-based fallback will be used.")
        self._ready.set()

    # ── Public interface ──────────────────────────────────────────────────────
    @property
    def active_model_name(self) -> str:
        try:
            return self._models[self._active_index].model_name
        except IndexError:
            return "none"

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Try each model in order; return first success or rule-based fallback."""
        for offset in range(len(self._models)):
            idx   = (self._active_index + offset) % len(self._models)
            model = self._models[idx]
            try:
                resp = model.generate(messages, temperature=temperature, max_tokens=max_tokens)
                if resp.success and resp.text.strip():
                    if offset != 0:
                        log.info("Switched to fallback model: %s", model.model_name)
                        self._active_index = idx
                    return resp
            except Exception as exc:
                log.warning("Model %s raised: %s", model.model_name, exc)

        log.error("All LLM models failed. Returning rule-based fallback.")
        return LLMResponse(
            text=_RULE_BASED_FALLBACK,
            model="rule-based",
            success=False,
            error="All models unavailable",
        )

    def chat(self, system: str, user: str, **kwargs) -> str:
        msgs = [
            LLMMessage(role="system", content=system),
            LLMMessage(role="user",   content=user),
        ]
        return self.generate(msgs, **kwargs).text

    def is_any_available(self) -> bool:
        return get_client().ping() and any(m.is_available() for m in self._models)


# ── Module-level singleton ────────────────────────────────────────────────────
_router: Optional[LLMRouter] = None
_router_lock = threading.Lock()


def get_router() -> LLMRouter:
    """Return the module-level singleton router (lazy init)."""
    global _router
    if _router is None:
        with _router_lock:
            if _router is None:
                _router = LLMRouter()
    return _router
