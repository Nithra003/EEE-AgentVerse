"""
agents/conversation_agent.py — General medical Q&A with sliding-window memory.
Persists conversation history to SQLite.
"""
from __future__ import annotations

from typing import List, Optional

from agents.base_agent import AgentResponse, BaseAgent
from ai.llm_router import get_router
from ai.base_llm import LLMMessage
from ai.prompt_templates import MEDICAL_QA, MISSED_DOSE
from database.engine import get_session
from database import repository as repo
from utils.logger import get_logger

log = get_logger(__name__)

_EMERGENCY_KW = [
    "chest pain", "heart attack", "can't breathe", "unconscious",
    "severe bleeding", "stroke", "overdose", "poisoning", "not breathing",
]
_WINDOW_SIZE = 10   # keep last N turns in context


class ConversationAgent(BaseAgent):
    """
    Multi-turn medical Q&A agent with memory.
    Detects emergencies and escalates immediately.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._history: List[LLMMessage] = []

    def process(self, user_input: str) -> AgentResponse:
        text = (user_input or "").strip()
        if not text:
            return AgentResponse(message="Please type your question.", success=False)

        # Emergency check
        if any(kw in text.lower() for kw in _EMERGENCY_KW):
            return AgentResponse(
                message=(
                    "🚨 **This sounds urgent.**\n\n"
                    "Please call emergency services immediately.\n\n"
                    "Do not wait — go to the nearest hospital emergency room."
                ),
                emergency=True,
            )

        # Persist user turn
        self._persist_turn("user", text)

        # Build context window
        messages = [LLMMessage(role="system", content=MEDICAL_QA.system)]
        for msg in self._history[-_WINDOW_SIZE:]:
            messages.append(msg)
        messages.append(LLMMessage(role="user", content=text))

        # Generate response
        router = get_router()
        resp   = router.generate(messages)
        reply  = resp.text or "I'm sorry, I couldn't process that. Please try again."

        # Update in-memory history
        self._history.append(LLMMessage(role="user",      content=text))
        self._history.append(LLMMessage(role="assistant", content=reply))

        # Persist assistant turn
        self._persist_turn("assistant", reply)

        return AgentResponse(message=reply, success=resp.success)

    def analyse_missed_dose(
        self,
        patient_name: str,
        medicine_name: str,
        missed_count: int,
        reason: str = "not specified",
    ) -> str:
        """Generate missed-dose guidance."""
        from ai.prompt_templates import MISSED_DOSE
        router = get_router()
        prompt = MISSED_DOSE.render_user(
            patient_name=patient_name,
            medicine_name=medicine_name,
            missed_count=missed_count,
            reason=reason,
        )
        return router.chat(MISSED_DOSE.system, prompt) or "Please consult your doctor."

    def reset(self) -> None:
        self._history.clear()

    def _persist_turn(self, role: str, content: str) -> None:
        if not self.user_id:
            return
        try:
            with get_session() as session:
                repo.add_conversation_turn(
                    session,
                    user_id=self.user_id,
                    session_id=self.session_id,
                    role=role,
                    content=content,
                    language=self.language,
                    agent_type="chat",
                )
        except Exception as exc:
            log.warning("Could not persist conversation turn: %s", exc)
