# tools.py - Agent-callable tools (actions the agent can perform)

import random
from datetime import datetime
from doctors import DOCTORS, AVAILABLE_SLOTS, SPECIALTY_INFO, SYMPTOM_MAP

# In-memory appointment store (no database needed)
APPOINTMENTS = {}


def find_specialist(symptoms: str) -> dict:
    """
    Tool: Analyse symptoms and return the best matching specialty + doctors.
    Agent calls this to DECIDE which specialist to recommend.
    """
    text = symptoms.lower()
    weights = {"high": 3, "medium": 2, "low": 1}
    scores = {}

    for specialty, levels in SYMPTOM_MAP.items():
        score = sum(
            weights[level]
            for level, keywords in levels.items()
            for kw in keywords if kw in text
        )
        if score > 0:
            scores[specialty] = score

    if not scores:
        specialty = "General Physician"
        confidence = 40
    else:
        specialty = max(scores, key=scores.get)
        confidence = min(int((scores[specialty] / 6) * 100), 95)

    doctors = DOCTORS.get(specialty, DOCTORS["General Physician"])
    info    = SPECIALTY_INFO.get(specialty, {"icon": "🏥", "desc": ""})

    return {
        "specialty":   specialty,
        "confidence":  confidence,
        "icon":        info["icon"],
        "description": info["desc"],
        "doctors":     [d["name"] for d in doctors],
        "doctor_details": doctors,
    }


def check_available_slots(doctor_name: str) -> dict:
    """
    Tool: Return available time slots for a given doctor.
    Agent calls this to show patient what slots are free.
    """
    # In a real system, booked slots would be filtered out
    booked = [apt["time"] for apt in APPOINTMENTS.values()
              if apt["doctor"] == doctor_name]
    available = [s for s in AVAILABLE_SLOTS if s not in booked]

    return {
        "doctor":    doctor_name,
        "available": available,
        "booked":    booked,
    }


def book_appointment(patient: dict, doctor: str, specialty: str, date: str, time: str) -> dict:
    """
    Tool: Confirm and store the appointment.
    Agent calls this as the final ACTION after all decisions are made.
    """
    apt_id = f"APT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    record = {
        "apt_id":    apt_id,
        "name":      patient["name"],
        "age":       patient["age"],
        "gender":    patient["gender"],
        "phone":     patient["phone"],
        "symptoms":  patient["symptoms"],
        "doctor":    doctor,
        "specialty": specialty,
        "date":      date,
        "time":      time,
        "booked_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }
    APPOINTMENTS[apt_id] = record
    return record


def get_appointment(apt_id: str) -> dict | None:
    """Tool: Retrieve a booked appointment by ID."""
    return APPOINTMENTS.get(apt_id)


def build_confirmation_text(apt: dict) -> str:
    """Tool: Generate downloadable confirmation text."""
    div = "=" * 45
    return (
        f"{div}\n"
        f"   ELDERCARE AI - APPOINTMENT CONFIRMATION\n"
        f"{div}\n"
        f"Appointment ID : {apt['apt_id']}\n"
        f"Patient Name   : {apt['name']}\n"
        f"Age / Gender   : {apt['age']} / {apt['gender']}\n"
        f"Mobile         : {apt['phone']}\n"
        f"Symptoms       : {apt['symptoms']}\n"
        f"{div}\n"
        f"Doctor         : {apt['doctor']}\n"
        f"Department     : {apt['specialty']}\n"
        f"Date           : {apt['date']}\n"
        f"Time           : {apt['time']}\n"
        f"{div}\n"
        f"Please arrive 10 minutes early with a valid ID.\n"
        f"Generated on   : {apt['booked_at']}\n"
        f"{div}\n"
    )
