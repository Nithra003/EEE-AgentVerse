"""
ai/base_llm.py — Abstract LLM interface (Liskov-safe contract).
Every model implementation must subclass BaseLLM.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LLMMessage:
    role: str      # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    text: str
    model: str
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0


class BaseLLM(ABC):
    """Abstract base for all LLM backends."""

    model_name: str = ""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the model can accept requests right now."""

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send messages and return a structured response."""

    def chat(self, system: str, user: str, **kwargs) -> str:
        """Convenience wrapper: system + single user turn → plain text."""
        msgs = [
            LLMMessage(role="system", content=system),
            LLMMessage(role="user",   content=user),
        ]
        resp = self.generate(msgs, **kwargs)
        return resp.text if resp.success else ""
