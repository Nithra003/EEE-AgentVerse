"""
utils.py - Utility functions for Family Notification Agent
ElderCare AI – Day 1 Single Agent Challenge
"""

import re
from datetime import datetime


# ──────────────────────────────────────────────
# Priority mapping for emergency types
# ──────────────────────────────────────────────
PRIORITY_MAP = {
    "Missed Medicine": "Medium",
    "High Blood Pressure": "High",
    "High Blood Sugar": "High",
    "Low Heart Rate": "High",
    "Fall Detected": "Critical",
    "Emergency SOS": "Critical",
}

PRIORITY_COLORS = {
    "Medium": "🟡",
    "High": "🔴",
    "Critical": "🚨",
}

EMERGENCY_TYPES = list(PRIORITY_MAP.keys())

RELATIONSHIP_OPTIONS = ["Son", "Daughter", "Spouse", "Caregiver", "Friend", "Other"]


def get_priority(emergency_type: str) -> str:
    """Return priority level based on emergency type."""
    return PRIORITY_MAP.get(emergency_type, "Medium")


def get_priority_badge(priority: str) -> str:
    """Return colored badge for priority."""
    return PRIORITY_COLORS.get(priority, "⚪")


def validate_phone(phone: str) -> bool:
    """Validate 10-digit phone number."""
    return bool(re.fullmatch(r"\d{10}", phone.strip()))


def validate_age(age: int) -> bool:
    """Validate age is between 1 and 120."""
    return 1 <= age <= 120


def validate_fields(patient_name, age, contact_name, relationship,
                    contact_number, location, emergency_type) -> list:
    """
    Validate all form fields.
    Returns a list of error messages (empty list = all valid).
    """
    errors = []

    if not patient_name.strip():
        errors.append("Patient name is required.")
    if not validate_age(age):
        errors.append("Age must be between 1 and 120.")
    if not contact_name.strip():
        errors.append("Emergency contact name is required.")
    if not relationship:
        errors.append("Relationship is required.")
    if not validate_phone(contact_number):
        errors.append("Contact number must be exactly 10 digits.")
    if not location.strip():
        errors.append("Current location is required.")
    if not emergency_type:
        errors.append("Please select an emergency type.")

    return errors


def get_current_datetime() -> tuple:
    """Return current date and time as formatted strings."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")


def generate_report_text(summary: dict) -> str:
    """Generate downloadable plain-text emergency report."""
    date, time = get_current_datetime()
    lines = [
        "=" * 50,
        "   ELDERCARE AI – EMERGENCY REPORT",
        "=" * 50,
        f"Report Generated : {date} {time}",
        "-" * 50,
        f"Patient Name     : {summary['patient_name']}",
        f"Age              : {summary['age']}",
        f"Emergency Type   : {summary['emergency_type']}",
        f"Priority Level   : {summary['priority']}",
        f"Location         : {summary['location']}",
        "-" * 50,
        f"Contact Person   : {summary['contact_name']}",
        f"Relationship     : {summary['relationship']}",
        f"Contact Number   : {summary['contact_number']}",
        "-" * 50,
        f"Notification Status : {summary['status']}",
        "=" * 50,
        "",
        "NOTIFICATION LOG:",
        "  ✅ SMS sent successfully.",
        "  ✅ Email notification sent.",
        "  ✅ Emergency contact notified.",
        "  ✅ Emergency services can now be contacted.",
        "",
        "=" * 50,
        "         ElderCare AI – Powered by AgentVerse",
        "=" * 50,
    ]
    return "\n".join(lines)


# ──────────────────────────────────────────────
# Future Integration Points (DO NOT IMPLEMENT)
# ──────────────────────────────────────────────
# TODO: Medicine Reminder Agent  – trigger when emergency_type == "Missed Medicine"
# TODO: Emergency Detection Agent – auto-detect fall/SOS from wearable sensor data
# TODO: Health Monitoring Agent   – stream real-time vitals (BP, sugar, heart rate)
# TODO: Appointment Booking Agent – auto-book doctor after High/Critical alert
# TODO: Prescription Explainer Agent – attach prescription info to notification
# TODO: Voice Companion Agent     – read out alert via text-to-speech
# TODO: Diet Planning Agent       – suggest diet after High BP / High Sugar alert
# TODO: Exercise Coach Agent      – send safe exercise plan post-recovery
# TODO: Hospital Navigation Agent – provide nearest hospital route on Critical alert
