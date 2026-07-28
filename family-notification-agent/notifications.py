"""
notifications.py - Notification logic for Family Notification Agent
ElderCare AI – Day 1 Single Agent Challenge
"""

import random
from utils import get_priority, get_current_datetime


def build_notification(patient_name: str, age: int, emergency_type: str,
                       location: str, contact_name: str,
                       relationship: str, contact_number: str) -> dict:
    """
    Build a structured notification dictionary from form data.
    """
    date, time = get_current_datetime()
    priority = get_priority(emergency_type)

    return {
        "patient_name": patient_name.strip(),
        "age": age,
        "emergency_type": emergency_type,
        "location": location.strip(),
        "date": date,
        "time": time,
        "contact_name": contact_name.strip(),
        "relationship": relationship,
        "contact_number": contact_number.strip(),
        "priority": priority,
        "status": "Sent",
    }


def simulate_notification_channels(priority: str) -> list:
    """
    Simulate sending notifications through multiple channels.
    Returns a list of status messages.
    """
    messages = [
        ("📩", "SMS sent successfully to emergency contact."),
        ("📧", "Email notification dispatched."),
        ("📞", "Emergency contact notified via call simulation."),
    ]

    if priority == "Critical":
        messages.append(("🚑", "Emergency services can now be contacted."))

    # Simulate occasional delivery delay (for realism)
    statuses = []
    for icon, msg in messages:
        delivered = random.choices(["success", "warning"], weights=[90, 10])[0]
        statuses.append((icon, msg, delivered))

    return statuses


def add_to_history(history: list, notification: dict) -> list:
    """
    Append a new notification record to the session history list.
    """
    record = {
        "Date": notification["date"],
        "Time": notification["time"],
        "Patient Name": notification["patient_name"],
        "Emergency Type": notification["emergency_type"],
        "Priority": notification["priority"],
        "Contact Person": notification["contact_name"],
        "Status": _simulate_delivery_status(),
    }
    history.append(record)
    return history


def _simulate_delivery_status() -> str:
    """Randomly simulate a delivery status for demo purposes."""
    return random.choices(
        ["Delivered", "Sent", "Failed"],
        weights=[70, 25, 5]
    )[0]


# ──────────────────────────────────────────────
# Future Integration Points (DO NOT IMPLEMENT)
# ──────────────────────────────────────────────
# TODO: Emergency Detection Agent – replace manual form with auto-detected events
# TODO: Health Monitoring Agent   – pass real-time vitals into build_notification()
# TODO: Voice Companion Agent     – call text-to-speech API with notification text
# TODO: Hospital Navigation Agent – append nearest hospital info to Critical alerts
