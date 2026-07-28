# doctors.py - Doctor data and slot management

DOCTORS = {
    "General Physician": [
        {"name": "Dr. Priya Sharma", "experience": "12 years", "rating": "4.8"},
        {"name": "Dr. Arjun Mehta",  "experience": "9 years",  "rating": "4.7"},
    ],
    "Cardiologist": [
        {"name": "Dr. Kumar Rajan", "experience": "18 years", "rating": "4.9"},
    ],
    "Orthopedic": [
        {"name": "Dr. Meena Pillai", "experience": "14 years", "rating": "4.8"},
    ],
    "Ophthalmologist": [
        {"name": "Dr. Suresh Nair", "experience": "11 years", "rating": "4.7"},
    ],
    "Dentist": [
        {"name": "Dr. Ravi Verma", "experience": "8 years", "rating": "4.6"},
    ],
    "Dermatologist": [
        {"name": "Dr. Divya Krishnan", "experience": "10 years", "rating": "4.8"},
    ],
}

AVAILABLE_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM",
    "11:30 AM", "02:00 PM", "03:00 PM", "04:30 PM",
]

# Weighted keyword mapping — high/medium/low priority per specialty
SYMPTOM_MAP = {
    "General Physician": {
        "high":   ["fever", "cold", "cough", "flu", "vomiting", "diarrhea", "loose motion", "typhoid", "dengue", "viral"],
        "medium": ["headache", "fatigue", "weakness", "nausea", "body ache", "chills", "sore throat", "runny nose", "loss of appetite"],
        "low":    ["tired", "unwell", "not feeling well"],
    },
    "Cardiologist": {
        "high":   ["chest pain", "heart attack", "cardiac", "palpitation", "irregular heartbeat", "angina"],
        "medium": ["breathless", "shortness of breath", "high bp", "blood pressure", "hypertension", "swollen legs", "dizziness"],
        "low":    ["heart", "bp", "pulse"],
    },
    "Orthopedic": {
        "high":   ["fracture", "broken bone", "slip disc", "sciatica", "ligament tear"],
        "medium": ["joint pain", "knee pain", "back pain", "spine", "shoulder pain", "neck pain", "hip pain", "arthritis"],
        "low":    ["knee", "bone", "joint", "back", "ankle", "wrist pain"],
    },
    "Ophthalmologist": {
        "high":   ["vision loss", "eye infection", "cataract", "glaucoma", "conjunctivitis"],
        "medium": ["blurred vision", "eye pain", "redness in eye", "itchy eyes", "watery eyes", "double vision"],
        "low":    ["eye", "vision", "blur", "glasses"],
    },
    "Dentist": {
        "high":   ["tooth pain", "toothache", "tooth decay", "root canal", "broken tooth"],
        "medium": ["gum pain", "gum bleeding", "swollen gum", "mouth ulcer", "cavity", "jaw pain"],
        "low":    ["tooth", "teeth", "gum", "dental", "mouth"],
    },
    "Dermatologist": {
        "high":   ["skin rash", "eczema", "psoriasis", "fungal infection", "ringworm", "hives", "skin allergy"],
        "medium": ["acne", "pimples", "itching", "dry skin", "hair loss", "dandruff", "nail infection"],
        "low":    ["skin", "rash", "itch", "allergy", "spot"],
    },
}

# Info shown on recommendation page
SPECIALTY_INFO = {
    "General Physician":  {"icon": "🩺", "desc": "Treats common illnesses, infections, and general health issues."},
    "Cardiologist":       {"icon": "❤️", "desc": "Specialist for heart, blood pressure, and cardiovascular conditions."},
    "Orthopedic":         {"icon": "🦴", "desc": "Specialist for bones, joints, muscles, and spine problems."},
    "Ophthalmologist":    {"icon": "👁️", "desc": "Specialist for eye diseases, vision problems, and eye care."},
    "Dentist":            {"icon": "🦷", "desc": "Specialist for teeth, gums, and oral health."},
    "Dermatologist":      {"icon": "🧴", "desc": "Specialist for skin, hair, and nail conditions."},
}


def get_doctors_for_specialty(specialty: str) -> list:
    """Return list of doctors for a given specialty."""
    return DOCTORS.get(specialty, DOCTORS["General Physician"])


def get_all_specialties() -> list:
    return list(DOCTORS.keys())
