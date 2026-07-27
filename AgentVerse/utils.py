# utils.py - Validation, AI recommendation, and helper utilities

import re
import random
from datetime import datetime

import google.generativeai as genai

from doctors import SYMPTOM_MAP, SPECIALTY_INFO, get_all_specialties


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_name(name: str) -> str | None:
    """Return error string or None if valid."""
    if not name or not name.strip():
        return "Full name is required."
    if len(name.strip()) < 2:
        return "Name must be at least 2 characters."
    return None


def validate_age(age) -> str | None:
    try:
        age = int(age)
        if age < 1 or age > 120:
            return "Age must be between 1 and 120."
    except (ValueError, TypeError):
        return "Please enter a valid age."
    return None


def validate_phone(phone: str) -> str | None:
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if not re.fullmatch(r"[6-9]\d{9}", cleaned):
        return "Enter a valid 10-digit Indian mobile number starting with 6-9."
    return None


def validate_symptoms(symptoms: str) -> str | None:
    if not symptoms or not symptoms.strip():
        return "Please describe your symptoms."
    return None


def validate_all(form: dict) -> list[str]:
    """Run all validations and return a list of error messages."""
    errors = []
    for fn, key in [
        (validate_name,     "name"),
        (validate_age,      "age"),
        (validate_phone,    "phone"),
        (validate_symptoms, "symptoms"),
    ]:
        err = fn(form.get(key, ""))
        if err:
            errors.append(err)
    if not form.get("date"):
        errors.append("Please select a preferred date.")
    if not form.get("time"):
        errors.append("Please select a preferred time slot.")
    if not form.get("doctor"):
        errors.append("Please select a doctor.")
    return errors


# ---------------------------------------------------------------------------
# Appointment ID generator
# ---------------------------------------------------------------------------

def generate_appointment_id() -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    serial = random.randint(1000, 9999)
    return f"APT-{date_str}-{serial}"


# ---------------------------------------------------------------------------
# Gemini AI – symptom analysis
# ---------------------------------------------------------------------------

def recommend_specialty_gemini(symptoms: str, api_key: str) -> tuple[str, str, int]:
    """
    Use Gemini to recommend a medical specialty.
    Returns (specialty, explanation, confidence_pct).
    Falls back to weighted keyword matching on any error.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        specialties = ", ".join(get_all_specialties())
        prompt = (
            f"A patient reports the following symptoms: \"{symptoms}\".\n"
            f"Available specialties: {specialties}.\n"
            "Reply in exactly two lines:\n"
            "Line 1: The single most suitable specialty name (exact match from the list).\n"
            "Line 2: A brief, patient-friendly explanation (1-2 sentences)."
        )

        response = model.generate_content(prompt)
        lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]

        specialty = lines[0] if lines else "General Physician"
        explanation = lines[1] if len(lines) > 1 else "Based on your symptoms, this specialist is recommended."

        if specialty not in get_all_specialties():
            specialty, confidence = _keyword_fallback(symptoms)
            explanation = "Recommended based on symptom analysis."
        else:
            confidence = 92  # Gemini result = high confidence

        return specialty, explanation, confidence

    except Exception as e:
        specialty, confidence = _keyword_fallback(symptoms)
        return specialty, f"AI unavailable – using smart keyword analysis. ({type(e).__name__})", confidence


def _keyword_fallback(symptoms: str) -> tuple[str, int]:
    """Weighted keyword scoring — returns (specialty, confidence_pct)."""
    text = symptoms.lower()
    weights = {"high": 3, "medium": 2, "low": 1}
    scores = {}
    for specialty, levels in SYMPTOM_MAP.items():
        score = 0
        for level, keywords in levels.items():
            for kw in keywords:
                if kw in text:
                    score += weights[level]
        if score > 0:
            scores[specialty] = score

    if not scores:
        return "General Physician", 40

    best = max(scores, key=scores.get)
    max_possible = 6  # rough normaliser
    confidence = min(int((scores[best] / max_possible) * 100), 95)
    return best, confidence


# ---------------------------------------------------------------------------
# Confirmation text builder
# ---------------------------------------------------------------------------

def build_confirmation_text(details: dict) -> str:
    divider = "=" * 45
    return (
        f"{divider}\n"
        f"   ELDERCARE AI – APPOINTMENT CONFIRMATION\n"
        f"{divider}\n"
        f"Appointment ID : {details['apt_id']}\n"
        f"Patient Name   : {details['name']}\n"
        f"Age / Gender   : {details['age']} / {details['gender']}\n"
        f"Mobile         : {details['phone']}\n"
        f"Symptoms       : {details['symptoms']}\n"
        f"{divider}\n"
        f"Doctor         : {details['doctor']}\n"
        f"Department     : {details['specialty']}\n"
        f"Date           : {details['date']}\n"
        f"Time           : {details['time']}\n"
        f"{divider}\n"
        f"Please arrive 10 minutes before your appointment.\n"
        f"Carry a valid ID and any previous medical records.\n"
        f"{divider}\n"
        f"Generated on   : {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
        f"{divider}\n\n"
        # ---------------------------------------------------------------
        # FUTURE INTEGRATION POINTS
        # ---------------------------------------------------------------
        # [ Medicine Reminder Agent ]   – schedule post-appointment reminders
        # [ Emergency Detection Agent ] – monitor vitals for emergencies
        # [ Prescription Explainer Agent ] – explain prescriptions in simple language
        # [ Health Monitoring Agent ]   – track ongoing health metrics
        # [ Family Notification Agent ] – notify family members of appointments
        # [ Voice Companion Agent ]     – voice-based interaction for elders
        # [ Diet Planning Agent ]       – personalised diet recommendations
        # [ Exercise Coach Agent ]      – safe exercise plans for seniors
        # [ Hospital Navigation Agent ] – guide patient inside hospital premises
        # ---------------------------------------------------------------
    )
