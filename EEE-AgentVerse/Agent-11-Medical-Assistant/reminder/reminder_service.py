"""
reminder/reminder_service.py — Business logic for reminder CRUD + scheduling.
All public methods are safe (never raise to callers).
"""
from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from database.engine import get_session
from database import repository as repo
from database.models import Medicine, Reminder
from reminder.scheduler import (
    add_daily_job, add_once_job, add_weekly_job,
    pause_job, remove_job, resume_job,
)
from config import (
    DEFAULT_AFTERNOON_TIME, DEFAULT_MORNING_TIME,
    DEFAULT_NIGHT_TIME, REMINDER_MISSED_THRESHOLD,
    REMINDER_SNOOZE_MINUTES,
)
from utils.logger import get_logger
from utils.date_utils import parse_time

log = get_logger(__name__)

_DAY_MAP = {
    "monday": "mon", "tuesday": "tue", "wednesday": "wed",
    "thursday": "thu", "friday": "fri", "saturday": "sat", "sunday": "sun",
    "mon": "mon", "tue": "tue", "wed": "wed", "thu": "thu",
    "fri": "fri", "sat": "sat", "sun": "sun",
}


def _job_id(reminder_id: int) -> str:
    return f"reminder_{reminder_id}"


def _fire_reminder(reminder_id: int) -> None:
    """Called by APScheduler when a reminder fires."""
    log.info("Reminder fired: id=%d", reminder_id)
    # In a Streamlit app, we write to a shared state file/DB so the UI can poll
    with get_session() as session:
        rem = repo.get_reminder(session, reminder_id)
        if rem and rem.status == "active":
            repo.log_reminder_action(session, reminder_id, "fired")


def create_reminder_for_medicine(
    user_id: int,
    medicine: Medicine,
) -> List[int]:
    """
    Auto-create reminders from a Medicine's morning/afternoon/night flags.
    Returns list of created reminder IDs.
    """
    created_ids: List[int] = []
    slots = []
    if medicine.morning:
        slots.append(DEFAULT_MORNING_TIME)
    if medicine.afternoon:
        slots.append(DEFAULT_AFTERNOON_TIME)
    if medicine.night:
        slots.append(DEFAULT_NIGHT_TIME)

    for slot_str in slots:
        t = parse_time(slot_str)
        if t is None:
            continue
        rem_id = _create_and_schedule(
            user_id=user_id,
            medicine_id=medicine.id,
            remind_time=t,
            frequency="daily",
        )
        if rem_id:
            created_ids.append(rem_id)

    return created_ids


def create_custom_reminder(
    user_id: int,
    remind_time: time,
    frequency: str = "daily",
    medicine_id: Optional[int] = None,
    remind_date: Optional[date] = None,
    days_of_week: Optional[List[int]] = None,
) -> Optional[int]:
    """Create a custom reminder and schedule it. Returns reminder ID or None."""
    return _create_and_schedule(
        user_id=user_id,
        medicine_id=medicine_id,
        remind_time=remind_time,
        frequency=frequency,
        remind_date=remind_date,
        days_of_week=days_of_week,
    )


def _create_and_schedule(
    user_id: int,
    medicine_id: Optional[int],
    remind_time: time,
    frequency: str,
    remind_date: Optional[date] = None,
    days_of_week: Optional[List[int]] = None,
) -> Optional[int]:
    try:
        with get_session() as session:
            rem = repo.create_reminder(
                session,
                user_id=user_id,
                remind_time=remind_time,
                frequency=frequency,
                medicine_id=medicine_id,
                remind_date=remind_date,
                days_of_week=days_of_week,
            )
            rem_id = rem.id

        # Schedule the APScheduler job
        jid = _job_id(rem_id)
        h, m = remind_time.hour, remind_time.minute

        if frequency == "daily":
            add_daily_job(jid, _fire_reminder, h, m, args=[rem_id])
        elif frequency == "weekly" and days_of_week:
            day_str = ",".join(
                _DAY_MAP.get(str(d), "mon") for d in days_of_week
            )
            add_weekly_job(jid, _fire_reminder, day_str, h, m, args=[rem_id])
        elif frequency == "once" and remind_date:
            run_at = datetime.combine(remind_date, remind_time)
            add_once_job(jid, _fire_reminder, run_at, args=[rem_id])

        with get_session() as session:
            repo.set_reminder_job_id(session, rem_id, jid)

        log.info("Created reminder id=%d freq=%s", rem_id, frequency)
        return rem_id
    except Exception as exc:
        log.error("Failed to create reminder: %s", exc)
        return None


def mark_taken(reminder_id: int, note: str = "") -> bool:
    try:
        with get_session() as session:
            repo.log_reminder_action(session, reminder_id, "taken", note)
        return True
    except Exception as exc:
        log.error("mark_taken failed: %s", exc)
        return False


def mark_missed(reminder_id: int) -> bool:
    try:
        with get_session() as session:
            repo.log_reminder_action(session, reminder_id, "missed")
            missed = repo.count_missed(session, reminder_id)
            if missed >= REMINDER_MISSED_THRESHOLD:
                log.warning(
                    "Reminder %d missed %d times — caregiver alert threshold reached.",
                    reminder_id, missed,
                )
        return True
    except Exception as exc:
        log.error("mark_missed failed: %s", exc)
        return False


def snooze_reminder(reminder_id: int) -> bool:
    try:
        snooze_until = datetime.now() + timedelta(minutes=REMINDER_SNOOZE_MINUTES)
        with get_session() as session:
            repo.update_reminder_status(session, reminder_id, "snoozed", snooze_until)
            repo.log_reminder_action(session, reminder_id, "snoozed")
        rem = _get_reminder(reminder_id)
        if rem:
            jid = _job_id(reminder_id)
            add_once_job(jid + "_snooze", _fire_reminder, snooze_until, args=[reminder_id])
        return True
    except Exception as exc:
        log.error("snooze_reminder failed: %s", exc)
        return False


def pause_reminder(reminder_id: int) -> bool:
    try:
        with get_session() as session:
            repo.update_reminder_status(session, reminder_id, "paused")
        pause_job(_job_id(reminder_id))
        return True
    except Exception as exc:
        log.error("pause_reminder failed: %s", exc)
        return False


def resume_reminder(reminder_id: int) -> bool:
    try:
        with get_session() as session:
            repo.update_reminder_status(session, reminder_id, "active")
        resume_job(_job_id(reminder_id))
        return True
    except Exception as exc:
        log.error("resume_reminder failed: %s", exc)
        return False


def delete_reminder(reminder_id: int) -> bool:
    try:
        remove_job(_job_id(reminder_id))
        with get_session() as session:
            rem = repo.get_reminder(session, reminder_id)
            if rem:
                session.delete(rem)
        return True
    except Exception as exc:
        log.error("delete_reminder failed: %s", exc)
        return False


def get_user_reminders(user_id: int, status: Optional[str] = None) -> List[Dict]:
    """Return serialisable list of reminder dicts for the UI."""
    try:
        with get_session() as session:
            rems = repo.get_reminders(session, user_id, status)
            result = []
            for r in rems:
                med_name = r.medicine.name if r.medicine else "General"
                result.append({
                    "id":          r.id,
                    "medicine":    med_name,
                    "time":        r.remind_time.strftime("%I:%M %p"),
                    "frequency":   r.frequency,
                    "status":      r.status,
                    "days":        json.loads(r.days_of_week) if r.days_of_week else [],
                    "remind_date": str(r.remind_date) if r.remind_date else "",
                })
            return result
    except Exception as exc:
        log.error("get_user_reminders failed: %s", exc)
        return []


def _get_reminder(reminder_id: int) -> Optional[Reminder]:
    try:
        with get_session() as session:
            return repo.get_reminder(session, reminder_id)
    except Exception:
        return None
