"""
Agent Bridge — one publish helper per communication flow.
Import and call these from each agent; never call event_bus directly.
"""

from shared.event_bus import publish, subscribe, latest  # re-export for convenience


# ── Publishers ────────────────────────────────────────────────────────────────

def prescription_to_reminder(patient_name: str, medicines: list[dict]) -> None:
    """Agent-4 → Agent-1: send extracted medicines as reminders."""
    publish("prescription_extracted", "Agent-4-Prescription-Explainer", {
        "patient_name": patient_name,
        "medicines":    medicines,   # list of {name, dosage, frequency, duration}
    })


def reminder_to_voice(patient_name: str, medicine: str, time: str) -> None:
    """Agent-1 → Agent-10: announce a medicine reminder."""
    publish("reminder_fired", "Agent-1-Medicine-Reminder", {
        "patient_name": patient_name,
        "medicine":     medicine,
        "time":         time,
    })


def health_report_to_diet_exercise(patient_name: str, age: int,
                                   condition: str, risk_level: str,
                                   recommendations: list[str]) -> None:
    """Agent-5 → Agent-7 & Agent-8: share health report summary."""
    publish("health_report_ready", "Agent-5-Health-Report", {
        "patient_name":    patient_name,
        "age":             age,
        "condition":       condition,
        "risk_level":      risk_level,
        "recommendations": recommendations,
    })


def emergency_to_family(patient_name: str, location: str,
                        risk_level: str, status: str) -> None:
    """Agent-2 → Agent-6: forward emergency alert."""
    publish("emergency_detected", "Agent-2-Emergency-Detection", {
        "patient_name": patient_name,
        "location":     location,
        "risk_level":   risk_level,
        "status":       status,
    })


def appointment_to_voice(patient_name: str, doctor: str,
                         specialty: str, date: str, time: str,
                         apt_id: str) -> None:
    """Agent-3 → Agent-10: announce confirmed appointment."""
    publish("appointment_confirmed", "Agent-3-Appointment-Booking", {
        "patient_name": patient_name,
        "doctor":       doctor,
        "specialty":    specialty,
        "date":         date,
        "time":         time,
        "apt_id":       apt_id,
    })


def mood_to_exercise(patient_name: str, mood: str, age: int) -> None:
    """Agent-9 → Agent-8: share mood so exercise coach can adapt plan."""
    publish("mood_checked_in", "Agent-9-Mood-Companion", {
        "patient_name": patient_name,
        "mood":         mood,
        "age":          age,
    })


# ── Subscriber helpers (used by receiving agents) ─────────────────────────────

def get_prescription_events(consumer: str = "Agent-1-Medicine-Reminder") -> list[dict]:
    return subscribe("prescription_extracted", consumer)


def get_reminder_events(consumer: str = "Agent-10-Voice-Assistant") -> list[dict]:
    return subscribe("reminder_fired", consumer)


def get_health_report_events(consumer: str) -> list[dict]:
    return subscribe("health_report_ready", consumer)


def get_emergency_events(consumer: str = "Agent-6-Family-Notifier") -> list[dict]:
    return subscribe("emergency_detected", consumer)


def get_appointment_events(consumer: str = "Agent-10-Voice-Assistant") -> list[dict]:
    return subscribe("appointment_confirmed", consumer)


def get_mood_events(consumer: str = "Agent-8-Exercise-Coach") -> list[dict]:
    return subscribe("mood_checked_in", consumer)
