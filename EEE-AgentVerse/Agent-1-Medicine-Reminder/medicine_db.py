"""
medicine_db.py — Medicine knowledge base for Medicine Reminder AI Agent
"""

from datetime import datetime

# ── Medicine database ─────────────────────────────────────────────────────────
MEDICINES = {
    "metformin": {
        "name": "Metformin", "type": "Diabetes",
        "food": "after food", "water": "with a full glass of water",
        "missed_advice": "Take it as soon as you remember with your next meal. Never double dose.",
        "skip_risk": "HIGH — Blood sugar may rise significantly.",
        "interactions": ["alcohol", "contrast dye"],
        "emergency_symptoms": ["severe nausea", "stomach pain", "difficulty breathing"],
    },
    "paracetamol": {
        "name": "Paracetamol", "type": "Pain / Fever",
        "food": "after food", "water": "with water",
        "missed_advice": "Take it when you remember. If it is close to next dose time, skip the missed dose.",
        "skip_risk": "LOW — Pain or fever may return.",
        "interactions": ["alcohol", "warfarin"],
        "emergency_symptoms": ["skin rash", "difficulty breathing", "swelling"],
    },
    "atorvastatin": {
        "name": "Atorvastatin", "type": "Cholesterol",
        "food": "any time", "water": "with water",
        "missed_advice": "Take it as soon as you remember. If almost time for next dose, skip.",
        "skip_risk": "MEDIUM — Cholesterol control may be affected.",
        "interactions": ["grapefruit juice", "certain antibiotics"],
        "emergency_symptoms": ["muscle pain", "dark urine", "yellowing of skin"],
    },
    "amlodipine": {
        "name": "Amlodipine", "type": "Blood Pressure",
        "food": "any time", "water": "with water",
        "missed_advice": "Take it as soon as you remember the same day. Skip if next day.",
        "skip_risk": "HIGH — Blood pressure may rise.",
        "interactions": ["grapefruit juice", "simvastatin"],
        "emergency_symptoms": ["severe dizziness", "chest pain", "rapid heartbeat"],
    },
    "aspirin": {
        "name": "Aspirin", "type": "Blood Thinner / Pain",
        "food": "after food", "water": "with water",
        "missed_advice": "Take it as soon as you remember. Do not double dose.",
        "skip_risk": "MEDIUM — Blood clot risk may increase.",
        "interactions": ["ibuprofen", "warfarin", "alcohol"],
        "emergency_symptoms": ["unusual bleeding", "black stools", "vomiting blood"],
    },
    "insulin": {
        "name": "Insulin", "type": "Diabetes",
        "food": "before food", "water": "injection",
        "missed_advice": "Contact your doctor immediately. Do not guess the dose.",
        "skip_risk": "CRITICAL — Blood sugar can become dangerously high.",
        "interactions": ["alcohol", "beta blockers"],
        "emergency_symptoms": ["dizziness", "sweating", "confusion", "shaking", "unconscious"],
    },
    "vitamin d": {
        "name": "Vitamin D", "type": "Supplement",
        "food": "after food", "water": "with water",
        "missed_advice": "Take it when you remember. It is safe to take with the next dose.",
        "skip_risk": "LOW — Occasional miss is not harmful.",
        "interactions": [],
        "emergency_symptoms": [],
    },
    "omeprazole": {
        "name": "Omeprazole", "type": "Acidity",
        "food": "before food", "water": "with water",
        "missed_advice": "Take it before your next meal. Do not double dose.",
        "skip_risk": "LOW — Acidity or heartburn may return.",
        "interactions": ["clopidogrel", "methotrexate"],
        "emergency_symptoms": ["severe stomach pain", "blood in stool"],
    },
}

def get_medicine(name: str) -> dict | None:
    return MEDICINES.get(name.lower().strip())

def get_generic(name: str) -> dict:
    return {
        "name": name.title(), "type": "General",
        "food": "as prescribed", "water": "with water",
        "missed_advice": "Take it as soon as you remember. Consult your doctor if unsure.",
        "skip_risk": "UNKNOWN — Please consult your doctor.",
        "interactions": [],
        "emergency_symptoms": [],
    }

# ── Adherence log (in-memory for demo) ───────────────────────────────────────
_LOG: list[dict] = []

def log_dose(patient: str, medicine: str, status: str, note: str = ""):
    _LOG.append({
        "patient":  patient,
        "medicine": medicine,
        "status":   status,   # taken / missed / skipped
        "time":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "note":     note,
    })

def get_log(patient: str = "") -> list[dict]:
    if patient:
        return [l for l in _LOG if l["patient"].lower() == patient.lower()]
    return _LOG

def get_adherence(patient: str) -> dict:
    logs   = get_log(patient)
    total  = len(logs)
    taken  = sum(1 for l in logs if l["status"] == "taken")
    missed = sum(1 for l in logs if l["status"] in ["missed", "skipped"])
    pct    = round((taken / total) * 100) if total > 0 else 0
    return {"total": total, "taken": taken, "missed": missed, "percentage": pct, "logs": logs}

def get_todays_log(patient: str) -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    return [l for l in get_log(patient) if l["time"].startswith(today)]

def check_missed_count(patient: str, medicine: str) -> int:
    logs = get_log(patient)
    return sum(1 for l in logs if l["medicine"].lower() == medicine.lower()
               and l["status"] in ["missed", "skipped"])
