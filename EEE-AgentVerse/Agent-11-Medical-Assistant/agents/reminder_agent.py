"""
agents/reminder_agent.py — Reminder creation, management, and notification dispatch.
"""
from __future__ import annotations

from datetime import time
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentResponse, BaseAgent
from reminder.reminder_service import (
    create_custom_reminder, delete_reminder, get_user_reminders,
    mark_missed, mark_taken, pause_reminder, resume_reminder, snooze_reminder,
)
from utils.logger import get_logger
from utils.date_utils import parse_time

log = get_logger(__name__)


class ReminderAgent(BaseAgent):
    """Manages reminder lifecycle for a user."""

    def process(self, user_input: str) -> AgentResponse:
        # Reminder agent is driven by UI actions, not free text
        return AgentResponse(message="Use the Reminders page to manage your reminders.")

    def create(
        self,
        remind_time_str: str,
        frequency: str = "daily",
        medicine_id: Optional[int] = None,
        days_of_week: Optional[List[int]] = None,
    ) -> AgentResponse:
        t = parse_time(remind_time_str)
        if t is None:
            return AgentResponse(message="Invalid time format. Use HH:MM or HH:MM AM/PM.", success=False)

        rem_id = create_custom_reminder(
            user_id=self.user_id or 0,
            remind_time=t,
            frequency=frequency,
            medicine_id=medicine_id,
            days_of_week=days_of_week,
        )
        if rem_id:
            return AgentResponse(
                message=f"✅ Reminder set for {remind_time_str} ({frequency}).",
                data={"reminder_id": rem_id},
            )
        return AgentResponse(message="Could not create reminder. Please try again.", success=False)

    def take(self, reminder_id: int) -> AgentResponse:
        ok = mark_taken(reminder_id)
        return AgentResponse(
            message="✅ Marked as taken! Great job! 💊" if ok else "Could not update reminder.",
            success=ok,
        )

    def miss(self, reminder_id: int) -> AgentResponse:
        ok = mark_missed(reminder_id)
        return AgentResponse(
            message="⚠️ Marked as missed. Please try to take your medicine on time." if ok else "Could not update.",
            success=ok,
        )

    def snooze(self, reminder_id: int) -> AgentResponse:
        ok = snooze_reminder(reminder_id)
        return AgentResponse(
            message="⏰ Snoozed for 10 minutes." if ok else "Could not snooze.",
            success=ok,
        )

    def pause(self, reminder_id: int) -> AgentResponse:
        ok = pause_reminder(reminder_id)
        return AgentResponse(message="⏸️ Reminder paused." if ok else "Could not pause.", success=ok)

    def resume(self, reminder_id: int) -> AgentResponse:
        ok = resume_reminder(reminder_id)
        return AgentResponse(message="▶️ Reminder resumed." if ok else "Could not resume.", success=ok)

    def delete(self, reminder_id: int) -> AgentResponse:
        ok = delete_reminder(reminder_id)
        return AgentResponse(message="🗑️ Reminder deleted." if ok else "Could not delete.", success=ok)

    def list_reminders(self, status: Optional[str] = None) -> List[Dict]:
        return get_user_reminders(self.user_id or 0, status)
