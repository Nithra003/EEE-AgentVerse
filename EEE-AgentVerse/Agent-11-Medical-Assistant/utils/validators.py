"""
utils/validators.py — Input validation helpers used across agents and UI.
All functions return (is_valid: bool, error_message: str).
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


def validate_username(value: str) -> tuple[bool, str]:
    v = value.strip()
    if len(v) < 3:
        return False, "Username must be at least 3 characters."
    if len(v) > 32:
        return False, "Username must be 32 characters or fewer."
    if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
        return False, "Username may only contain letters, digits, and underscores."
    return True, ""


def validate_password(value: str) -> tuple[bool, str]:
    if len(value) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


def validate_age(value: Any) -> tuple[bool, str]:
    try:
        age = int(value)
    except (TypeError, ValueError):
        return False, "Age must be a whole number."
    if not (1 <= age <= 120):
        return False, "Age must be between 1 and 120."
    return True, ""


def validate_phone(value: str) -> tuple[bool, str]:
    phone = re.sub(r"[\s\-\(\)]", "", str(value))
    if re.fullmatch(r"[6-9]\d{9}", phone):
        return True, ""
    if re.fullmatch(r"\+?\d{7,15}", phone):
        return True, ""
    return False, "Enter a valid phone number (10 digits for India, or international format)."


def validate_date_string(value: str, fmt: str = "%Y-%m-%d") -> tuple[bool, str]:
    try:
        datetime.strptime(value.strip(), fmt)
        return True, ""
    except ValueError:
        return False, f"Date must be in {fmt} format."


def validate_time_string(value: str) -> tuple[bool, str]:
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p"):
        try:
            datetime.strptime(value.strip(), fmt)
            return True, ""
        except ValueError:
            continue
    return False, "Time must be in HH:MM or HH:MM AM/PM format."


def validate_medicine_name(value: str) -> tuple[bool, str]:
    v = value.strip()
    if len(v) < 2:
        return False, "Medicine name must be at least 2 characters."
    if len(v) > 128:
        return False, "Medicine name is too long."
    return True, ""


def validate_duration_days(value: Any) -> tuple[bool, str]:
    try:
        days = int(value)
    except (TypeError, ValueError):
        return False, "Duration must be a whole number of days."
    if days <= 0:
        return False, "Duration must be greater than zero."
    if days > 3650:
        return False, "Duration cannot exceed 10 years."
    return True, ""


def sanitize_text(value: str, max_len: int = 1000) -> str:
    """Strip leading/trailing whitespace and truncate to max_len."""
    return value.strip()[:max_len]
