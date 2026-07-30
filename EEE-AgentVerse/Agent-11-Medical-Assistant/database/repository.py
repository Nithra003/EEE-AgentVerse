"""
database/repository.py — Generic CRUD repository + domain-specific queries.
No raw SQL anywhere else in the codebase.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import and_, desc, func as sa_func
from sqlalchemy.orm import Session, joinedload

from database.models import (
    Appointment, ConversationHistory, Medicine,
    Prescription, Reminder, ReminderLog, User,
)
from utils.logger import get_logger

log = get_logger(__name__)
T = TypeVar("T")


# ── Generic helpers ───────────────────────────────────────────────────────────
def _get_by_id(session: Session, model: Type[T], pk: int) -> Optional[T]:
    return session.get(model, pk)


def _delete(session: Session, obj: Any) -> None:
    session.delete(obj)


# ── User repository ───────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(
    session: Session,
    username: str,
    password: str,
    full_name: str,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    phone: Optional[str] = None,
    language: str = "en",
) -> User:
    user = User(
        username=username.lower().strip(),
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        age=age,
        gender=gender,
        phone=phone,
        language=language,
    )
    session.add(user)
    session.flush()
    log.info("Created user: %s", user.username)
    return user


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return (
        session.query(User)
        .filter(User.username == username.lower().strip())
        .first()
    )


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(session, username)
    if user and user.password_hash == hash_password(password):
        return user
    return None


def update_user_profile(
    session: Session,
    user_id: int,
    full_name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    phone: Optional[str] = None,
    language: Optional[str] = None,
    theme: Optional[str] = None,
) -> Optional[User]:
    user = _get_by_id(session, User, user_id)
    if not user:
        return None
    if full_name is not None:
        user.full_name = full_name
    if age is not None:
        user.age = age
    if gender is not None:
        user.gender = gender
    if phone is not None:
        user.phone = phone
    if language is not None:
        user.language = language
    if theme is not None:
        user.theme = theme
    session.flush()
    return user


# ── Prescription repository ───────────────────────────────────────────────────
def create_prescription(session: Session, user_id: int, **kwargs: Any) -> Prescription:
    rx = Prescription(user_id=user_id, **kwargs)
    session.add(rx)
    session.flush()
    log.info("Created prescription id=%d for user_id=%d", rx.id, user_id)
    return rx


def get_prescriptions(session: Session, user_id: int, limit: int = 50) -> List[Prescription]:
    return (
        session.query(Prescription)
        .options(joinedload(Prescription.medicines))
        .filter(Prescription.user_id == user_id)
        .order_by(desc(Prescription.created_at))
        .limit(limit)
        .all()
    )


def get_prescription(session: Session, rx_id: int) -> Optional[Prescription]:
    return _get_by_id(session, Prescription, rx_id)


# ── Medicine repository ───────────────────────────────────────────────────────
def create_medicine(session: Session, user_id: int, **kwargs: Any) -> Medicine:
    med = Medicine(user_id=user_id, **kwargs)
    session.add(med)
    session.flush()
    return med


def get_medicines(session: Session, user_id: int) -> List[Medicine]:
    return (
        session.query(Medicine)
        .filter(Medicine.user_id == user_id)
        .order_by(desc(Medicine.created_at))
        .all()
    )


def get_active_medicines(session: Session, user_id: int) -> List[Medicine]:
    """Return medicines whose end_date is in the future or unset."""
    today = date.today()
    return (
        session.query(Medicine)
        .filter(
            Medicine.user_id == user_id,
            (Medicine.end_date == None) | (Medicine.end_date >= today),
        )
        .order_by(Medicine.name)
        .all()
    )


def get_medicine(session: Session, med_id: int) -> Optional[Medicine]:
    return _get_by_id(session, Medicine, med_id)


def update_medicine(session: Session, med_id: int, **kwargs: Any) -> Optional[Medicine]:
    med = _get_by_id(session, Medicine, med_id)
    if not med:
        return None
    for k, v in kwargs.items():
        if hasattr(med, k):
            setattr(med, k, v)
    session.flush()
    return med


def delete_medicine(session: Session, med_id: int) -> bool:
    med = _get_by_id(session, Medicine, med_id)
    if not med:
        return False
    _delete(session, med)
    return True


# ── Reminder repository ───────────────────────────────────────────────────────
def create_reminder(
    session: Session,
    user_id: int,
    remind_time: time,
    frequency: str = "daily",
    medicine_id: Optional[int] = None,
    remind_date: Optional[date] = None,
    days_of_week: Optional[List[int]] = None,
) -> Reminder:
    rem = Reminder(
        user_id=user_id,
        medicine_id=medicine_id,
        remind_time=remind_time,
        remind_date=remind_date,
        frequency=frequency,
        days_of_week=json.dumps(days_of_week) if days_of_week else None,
        status="active",
    )
    session.add(rem)
    session.flush()
    return rem


def get_reminders(
    session: Session,
    user_id: int,
    status: Optional[str] = None,
) -> List[Reminder]:
    q = (
        session.query(Reminder)
        .options(joinedload(Reminder.medicine))
        .filter(Reminder.user_id == user_id)
    )
    if status:
        q = q.filter(Reminder.status == status)
    return q.order_by(Reminder.remind_time).all()


def get_reminder(session: Session, rem_id: int) -> Optional[Reminder]:
    return _get_by_id(session, Reminder, rem_id)


def update_reminder_status(
    session: Session, rem_id: int, status: str, snooze_until: Optional[datetime] = None
) -> Optional[Reminder]:
    rem = _get_by_id(session, Reminder, rem_id)
    if not rem:
        return None
    rem.status = status
    if snooze_until:
        rem.snooze_until = snooze_until
    session.flush()
    return rem


def set_reminder_job_id(session: Session, rem_id: int, job_id: str) -> None:
    rem = _get_by_id(session, Reminder, rem_id)
    if rem:
        rem.scheduler_job_id = job_id
        session.flush()


def log_reminder_action(
    session: Session, reminder_id: int, action: str, note: str = ""
) -> ReminderLog:
    entry = ReminderLog(
        reminder_id=reminder_id,
        fired_at=datetime.now(),
        action=action,
        note=note,
    )
    session.add(entry)
    session.flush()
    return entry


def get_reminder_logs(
    session: Session, user_id: int, limit: int = 100
) -> List[ReminderLog]:
    return (
        session.query(ReminderLog)
        .join(Reminder)
        .filter(Reminder.user_id == user_id)
        .order_by(desc(ReminderLog.fired_at))
        .limit(limit)
        .all()
    )


def count_missed(session: Session, reminder_id: int) -> int:
    return (
        session.query(ReminderLog)
        .filter(
            and_(
                ReminderLog.reminder_id == reminder_id,
                ReminderLog.action == "missed",
            )
        )
        .count()
    )


# ── Appointment repository ────────────────────────────────────────────────────
def create_appointment(
    session: Session,
    user_id: int,
    apt_ref: str,
    doctor_name: str,
    apt_date: date,
    apt_time: time,
    specialty: Optional[str] = None,
    hospital: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
) -> Appointment:
    apt = Appointment(
        user_id=user_id,
        apt_ref=apt_ref,
        doctor_name=doctor_name,
        specialty=specialty,
        hospital=hospital,
        apt_date=apt_date,
        apt_time=apt_time,
        symptoms=symptoms,
        notes=notes,
        status="confirmed",
    )
    session.add(apt)
    session.flush()
    log.info("Booked appointment %s for user_id=%d", apt_ref, user_id)
    return apt


def get_appointments(
    session: Session, user_id: int, upcoming_only: bool = False
) -> List[Appointment]:
    q = session.query(Appointment).filter(Appointment.user_id == user_id)
    if upcoming_only:
        q = q.filter(Appointment.apt_date >= date.today())
    return q.order_by(Appointment.apt_date, Appointment.apt_time).all()


def get_appointment_by_ref(session: Session, apt_ref: str) -> Optional[Appointment]:
    return session.query(Appointment).filter(Appointment.apt_ref == apt_ref).first()


def cancel_appointment(session: Session, apt_id: int) -> bool:
    apt = _get_by_id(session, Appointment, apt_id)
    if not apt:
        return False
    apt.status = "cancelled"
    session.flush()
    return True


# ── Conversation history repository ──────────────────────────────────────────
def add_conversation_turn(
    session: Session,
    user_id: int,
    session_id: str,
    role: str,
    content: str,
    language: Optional[str] = None,
    agent_type: Optional[str] = None,
) -> ConversationHistory:
    turn = ConversationHistory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        language=language,
        agent_type=agent_type,
    )
    session.add(turn)
    session.flush()
    return turn


def get_conversation(
    session: Session,
    user_id: int,
    session_id: str,
    limit: int = 20,
) -> List[ConversationHistory]:
    return (
        session.query(ConversationHistory)
        .filter(
            and_(
                ConversationHistory.user_id == user_id,
                ConversationHistory.session_id == session_id,
            )
        )
        .order_by(ConversationHistory.created_at)
        .limit(limit)
        .all()
    )


def get_adherence_stats(session: Session, user_id: int) -> Dict[str, int]:
    """Return taken/missed/snoozed counts — single aggregated query, no N+1."""
    rows = (
        session.query(ReminderLog.action, sa_func.count(ReminderLog.id))
        .join(Reminder)
        .filter(Reminder.user_id == user_id)
        .group_by(ReminderLog.action)
        .all()
    )
    stats: Dict[str, int] = {"taken": 0, "missed": 0, "snoozed": 0, "total": 0}
    for action, count in rows:
        key = action if action in stats else "missed"
        stats[key] += count
        stats["total"] += count
    total = stats["total"]
    stats["percentage"] = round(stats["taken"] / total * 100) if total else 0
    return stats
