"""
ai/model_implementations.py — Qwen3, DeepSeek-R1, Llama3.1 Ollama backends.
All share a single OllamaClient singleton to avoid redundant connections.
"""
from __future__ import annotations

import re
from typing import List

from ai.base_llm import BaseLLM, LLMMessage, LLMResponse
from ai.ollama_client import get_client
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE
from utils.logger import get_logger

log = get_logger(__name__)

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _build_messages(messages: List[LLMMessage]) -> List[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


def _strip_think_tags(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def _call_ollama(
    model_name: str,
    messages: List[LLMMessage],
    temperature: float,
    max_tokens: int,
) -> LLMResponse:
    try:
        raw  = get_client().chat(
            model=model_name,
            messages=_build_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = _strip_think_tags(raw.get("message", {}).get("content", ""))
        return LLMResponse(text=text, model=model_name, success=True)
    except Exception as exc:
        log.warning("Ollama call failed for %s: %s", model_name, exc)
        return LLMResponse(text="", model=model_name, success=False, error=str(exc))


class QwenModel(BaseLLM):
    model_name = "qwen3"

    def is_available(self) -> bool:
        return get_client().is_model_available(self.model_name)

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ) -> LLMResponse:
        return _call_ollama(self.model_name, messages, temperature, max_tokens)


class DeepSeekModel(BaseLLM):
    model_name = "deepseek-r1"

    def is_available(self) -> bool:
        return get_client().is_model_available(self.model_name)

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ) -> LLMResponse:
        return _call_ollama(self.model_name, messages, temperature, max_tokens)


class LlamaModel(BaseLLM):
    model_name = "llama3.1"

    def is_available(self) -> bool:
        return get_client().is_model_available(self.model_name)

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ) -> LLMResponse:
        return _call_ollama(self.model_name, messages, temperature, max_tokens)
