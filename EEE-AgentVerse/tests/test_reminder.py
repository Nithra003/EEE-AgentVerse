"""
tests/test_reminder.py — Reminder service tests (Agent-1 + Agent-11).
"""
from __future__ import annotations

import sys
from datetime import date, time, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Agent-1-Medicine-Reminder"))
sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-1 — medicine_db adherence (reminder-related)
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent1Reminders:
    def setup_method(self):
        import medicine_db
        medicine_db._LOG.clear()

    def test_log_taken_increments_adherence(self):
        from medicine_db import log_dose, get_adherence
        for _ in range(4):
            log_dose("Alice", "Metformin", "taken")
        log_dose("Alice", "Metformin", "missed")
        stats = get_adherence("Alice")
        assert stats["taken"] == 4
        assert stats["missed"] == 1
        assert stats["percentage"] == 80

    def test_log_skipped_counts_as_missed(self):
        from medicine_db import log_dose, get_adherence
        log_dose("Bob", "Aspirin", "skipped")
        stats = get_adherence("Bob")
        assert stats["missed"] == 1

    def test_check_missed_count_threshold(self):
        from medicine_db import log_dose, check_missed_count
        for _ in range(3):
            log_dose("Carol", "Insulin", "missed")
        assert check_missed_count("Carol", "Insulin") == 3

    def test_get_todays_log_only_today(self):
        from medicine_db import log_dose, get_todays_log
        log_dose("Dave", "Vitamin D", "taken")
        logs = get_todays_log("Dave")
        assert all(l["patient"] == "Dave" for l in logs)

    def test_all_medicines_have_emergency_symptoms_field(self):
        from medicine_db import MEDICINES
        for name, data in MEDICINES.items():
            assert "emergency_symptoms" in data, f"{name} missing emergency_symptoms"

    def test_insulin_skip_risk_critical(self):
        from medicine_db import get_medicine
        insulin = get_medicine("insulin")
        assert "CRITICAL" in insulin["skip_risk"]

    def test_vitamin_d_skip_risk_low(self):
        from medicine_db import get_medicine
        vd = get_medicine("vitamin d")
        assert "LOW" in vd["skip_risk"]


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-11 — reminder_service.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent11ReminderService:
    """Tests for reminder_service using mocked DB and scheduler."""

    def _mock_session(self):
        session = MagicMock()
        session.__enter__ = MagicMock(return_value=session)
        session.__exit__ = MagicMock(return_value=False)
        return session

    def test_mark_taken_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.log_reminder_action.return_value = MagicMock()
            from reminder.reminder_service import mark_taken
            result = mark_taken(1, "taken manually")
        assert result is True

    def test_mark_missed_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.log_reminder_action.return_value = MagicMock()
            mock_repo.count_missed.return_value = 1
            from reminder.reminder_service import mark_missed
            result = mark_missed(1)
        assert result is True

    def test_mark_taken_db_error_returns_false(self):
        with patch("reminder.reminder_service.get_session", side_effect=Exception("DB error")):
            from reminder.reminder_service import mark_taken
            result = mark_taken(999)
        assert result is False

    def test_mark_missed_db_error_returns_false(self):
        with patch("reminder.reminder_service.get_session", side_effect=Exception("DB error")):
            from reminder.reminder_service import mark_missed
            result = mark_missed(999)
        assert result is False

    def test_pause_reminder_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo, \
             patch("reminder.reminder_service.pause_job") as mock_pause:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.update_reminder_status.return_value = MagicMock()
            from reminder.reminder_service import pause_reminder
            result = pause_reminder(1)
        assert result is True

    def test_resume_reminder_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo, \
             patch("reminder.reminder_service.resume_job") as mock_resume:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.update_reminder_status.return_value = MagicMock()
            from reminder.reminder_service import resume_reminder
            result = resume_reminder(1)
        assert result is True

    def test_delete_reminder_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo, \
             patch("reminder.reminder_service.remove_job"):
            mock_session = MagicMock()
            mock_gs.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_rem = MagicMock()
            mock_repo.get_reminder.return_value = mock_rem
            from reminder.reminder_service import delete_reminder
            result = delete_reminder(1)
        assert result is True

    def test_get_user_reminders_empty(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.get_reminders.return_value = []
            from reminder.reminder_service import get_user_reminders
            result = get_user_reminders(1)
        assert result == []

    def test_get_user_reminders_with_data(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_rem = MagicMock()
            mock_rem.id = 1
            mock_rem.medicine = MagicMock()
            mock_rem.medicine.name = "Metformin"
            mock_rem.remind_time = time(8, 0)
            mock_rem.frequency = "daily"
            mock_rem.status = "active"
            mock_rem.days_of_week = None
            mock_rem.remind_date = None
            mock_repo.get_reminders.return_value = [mock_rem]
            from reminder.reminder_service import get_user_reminders
            result = get_user_reminders(1)
        assert len(result) == 1
        assert result[0]["medicine"] == "Metformin"

    def test_job_id_format(self):
        from reminder.reminder_service import _job_id
        assert _job_id(42) == "reminder_42"

    def test_create_reminder_for_medicine_morning_only(self):
        with patch("reminder.reminder_service._create_and_schedule", return_value=1) as mock_create:
            med = MagicMock()
            med.id = 1
            med.morning = True
            med.afternoon = False
            med.night = False
            from reminder.reminder_service import create_reminder_for_medicine
            ids = create_reminder_for_medicine(user_id=1, medicine=med)
        assert len(ids) == 1
        assert mock_create.call_count == 1

    def test_create_reminder_for_medicine_all_slots(self):
        with patch("reminder.reminder_service._create_and_schedule", return_value=1) as mock_create:
            med = MagicMock()
            med.id = 1
            med.morning = True
            med.afternoon = True
            med.night = True
            from reminder.reminder_service import create_reminder_for_medicine
            ids = create_reminder_for_medicine(user_id=1, medicine=med)
        assert len(ids) == 3
        assert mock_create.call_count == 3

    def test_snooze_reminder_success(self):
        with patch("reminder.reminder_service.get_session") as mock_gs, \
             patch("reminder.reminder_service.repo") as mock_repo, \
             patch("reminder.reminder_service._get_reminder") as mock_get, \
             patch("reminder.reminder_service.add_once_job"):
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.update_reminder_status.return_value = MagicMock()
            mock_repo.log_reminder_action.return_value = MagicMock()
            mock_get.return_value = MagicMock()
            from reminder.reminder_service import snooze_reminder
            result = snooze_reminder(1)
        assert result is True
