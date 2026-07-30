"""
appointment/appointment_service.py — Appointment booking business logic.
Persists to SQLite; generates unique reference IDs.
"""
from __future__ import annotations

import random
import string
from datetime import date, datetime, time
from typing import Dict, List, Optional

from database.engine import get_session
from database import repository as repo
from database.models import Appointment
from utils.logger import get_logger
from utils.date_utils import parse_date, parse_time

log = get_logger(__name__)


def _generate_ref() -> str:
    ts  = datetime.now().strftime("%Y%m%d")
    rnd = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"APT-{ts}-{rnd}"


def book_appointment(
    user_id: int,
    doctor_name: str,
    apt_date: date,
    apt_time: time,
    specialty: Optional[str] = None,
    hospital: Optional[str] = None,
    symptoms: Optional[str] = None,
    notes: Optional[str] = None,
) -> Optional[Dict]:
    """
    Persist a new appointment and return a serialisable dict.
    Returns None on failure.
    """
    try:
        apt_ref = _generate_ref()
        with get_session() as session:
            apt = repo.create_appointment(
                session,
                user_id=user_id,
                apt_ref=apt_ref,
                doctor_name=doctor_name,
                apt_date=apt_date,
                apt_time=apt_time,
                specialty=specialty,
                hospital=hospital,
                symptoms=symptoms,
                notes=notes,
            )
            return _serialise(apt)
    except Exception as exc:
        log.error("book_appointment failed: %s", exc)
        return None


def cancel_appointment(apt_id: int) -> bool:
    try:
        with get_session() as session:
            return repo.cancel_appointment(session, apt_id)
    except Exception as exc:
        log.error("cancel_appointment failed: %s", exc)
        return False


def get_user_appointments(user_id: int, upcoming_only: bool = False) -> List[Dict]:
    try:
        with get_session() as session:
            apts = repo.get_appointments(session, user_id, upcoming_only)
            return [_serialise(a) for a in apts]
    except Exception as exc:
        log.error("get_user_appointments failed: %s", exc)
        return []


def build_confirmation_text(apt: Dict) -> str:
    div = "=" * 48
    return (
        f"{div}\n"
        f"   AI MEDICAL ASSISTANT — APPOINTMENT CONFIRMATION\n"
        f"{div}\n"
        f"Reference      : {apt.get('apt_ref','')}\n"
        f"Doctor         : {apt.get('doctor_name','')}\n"
        f"Specialty      : {apt.get('specialty','')}\n"
        f"Hospital       : {apt.get('hospital','City Medical Centre')}\n"
        f"Date           : {apt.get('apt_date','')}\n"
        f"Time           : {apt.get('apt_time','')}\n"
        f"Symptoms       : {apt.get('symptoms','')}\n"
        f"Status         : {apt.get('status','confirmed').upper()}\n"
        f"{div}\n"
        f"Please arrive 10 minutes early with a valid photo ID.\n"
        f"Generated on   : {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"{div}\n"
    )


def _serialise(apt: Appointment) -> Dict:
    return {
        "id":          apt.id,
        "apt_ref":     apt.apt_ref,
        "doctor_name": apt.doctor_name,
        "specialty":   apt.specialty or "",
        "hospital":    apt.hospital or "City Medical Centre",
        "apt_date":    str(apt.apt_date),
        "apt_time":    apt.apt_time.strftime("%I:%M %p") if apt.apt_time else "",
        "symptoms":    apt.symptoms or "",
        "status":      apt.status,
        "notes":       apt.notes or "",
        "created_at":  str(apt.created_at),
    }
