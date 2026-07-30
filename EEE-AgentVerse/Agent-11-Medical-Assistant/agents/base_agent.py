"""
agents/base_agent.py — Abstract Agent interface (SOLID: Open/Closed Principle).
All agents implement perceive → think → act → respond.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentResponse:
    message: str
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    emergency: bool = False
    hint: str = ""


class BaseAgent(ABC):
    """
    Abstract base for all agents.
    Subclasses implement the perceive/think/act cycle.
    """

    def __init__(
        self,
        user_id: Optional[int] = None,
        language: str = "en",
        session_id: Optional[str] = None,
    ) -> None:
        self.user_id    = user_id
        self.language   = language
        self.session_id = session_id or "default"

    @abstractmethod
    def process(self, user_input: str) -> AgentResponse:
        """Main entry point: receive input, return structured response."""

    def reset(self) -> None:
        """Reset agent state. Override in stateful agents."""
        pass
