"""
appointment/doctor_registry.py — Doctor data, specialty mapping, symptom analysis.
Self-contained; no external dependencies.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional


class DoctorInfo(NamedTuple):
    name: str
    experience: str
    rating: str
    hospital: str = "City Medical Centre"


class SpecialtyInfo(NamedTuple):
    icon: str
    description: str
    emergency_keywords: List[str]


DOCTORS: Dict[str, List[DoctorInfo]] = {
    "General Physician": [
        DoctorInfo("Dr. Priya Sharma",   "12 years", "4.8"),
        DoctorInfo("Dr. Arjun Mehta",    "9 years",  "4.7"),
    ],
    "Cardiologist": [
        DoctorInfo("Dr. Kumar Rajan",    "18 years", "4.9"),
        DoctorInfo("Dr. Anita Nair",     "15 years", "4.8"),
    ],
    "Orthopedic": [
        DoctorInfo("Dr. Meena Pillai",   "14 years", "4.8"),
        DoctorInfo("Dr. Suresh Iyer",    "11 years", "4.7"),
    ],
    "Ophthalmologist": [
        DoctorInfo("Dr. Suresh Nair",    "11 years", "4.7"),
    ],
    "Dentist": [
        DoctorInfo("Dr. Ravi Verma",     "8 years",  "4.6"),
    ],
    "Dermatologist": [
        DoctorInfo("Dr. Divya Krishnan", "10 years", "4.8"),
    ],
    "Neurologist": [
        DoctorInfo("Dr. Ramesh Gupta",   "16 years", "4.9"),
    ],
    "Gastroenterologist": [
        DoctorInfo("Dr. Lakshmi Rao",    "13 years", "4.7"),
    ],
    "Pulmonologist": [
        DoctorInfo("Dr. Vijay Menon",    "12 years", "4.8"),
    ],
    "Endocrinologist": [
        DoctorInfo("Dr. Shalini Patel",  "14 years", "4.8"),
    ],
    "Psychiatrist": [
        DoctorInfo("Dr. Arun Bose",      "10 years", "4.7"),
    ],
    "ENT Specialist": [
        DoctorInfo("Dr. Kavitha Reddy",  "9 years",  "4.6"),
    ],
}

SPECIALTY_INFO: Dict[str, SpecialtyInfo] = {
    "General Physician":  SpecialtyInfo("🩺", "Treats common illnesses and general health issues.", ["fever", "cold", "flu"]),
    "Cardiologist":       SpecialtyInfo("❤️", "Heart, blood pressure, and cardiovascular conditions.", ["chest pain", "heart attack", "palpitation"]),
    "Orthopedic":         SpecialtyInfo("🦴", "Bones, joints, muscles, and spine problems.", ["fracture", "joint pain", "back pain"]),
    "Ophthalmologist":    SpecialtyInfo("👁️", "Eye diseases, vision problems, and eye care.", ["vision loss", "eye pain", "cataract"]),
    "Dentist":            SpecialtyInfo("🦷", "Teeth, gums, and oral health.", ["toothache", "gum pain", "cavity"]),
    "Dermatologist":      SpecialtyInfo("🧴", "Skin, hair, and nail conditions.", ["rash", "eczema", "acne"]),
    "Neurologist":        SpecialtyInfo("🧠", "Brain, spine, and nervous system disorders.", ["seizure", "migraine", "numbness"]),
    "Gastroenterologist": SpecialtyInfo("🫁", "Digestive system and gastrointestinal conditions.", ["stomach pain", "acid reflux", "ibs"]),
    "Pulmonologist":      SpecialtyInfo("🫁", "Lungs and respiratory conditions.", ["asthma", "copd", "breathless"]),
    "Endocrinologist":    SpecialtyInfo("⚗️", "Hormonal and metabolic conditions including diabetes.", ["diabetes", "thyroid", "hormone"]),
    "Psychiatrist":       SpecialtyInfo("🧘", "Mental health, anxiety, depression, and behavioural conditions.", ["anxiety", "depression", "insomnia"]),
    "ENT Specialist":     SpecialtyInfo("👂", "Ear, nose, and throat conditions.", ["ear pain", "sinus", "tonsil"]),
}

SYMPTOM_MAP: Dict[str, Dict[str, List[str]]] = {
    "General Physician":  {"high": ["fever","cold","cough","flu","vomiting","diarrhea","typhoid","dengue","viral"], "medium": ["headache","fatigue","weakness","nausea","body ache","chills","sore throat"], "low": ["tired","unwell"]},
    "Cardiologist":       {"high": ["chest pain","heart attack","cardiac","palpitation","irregular heartbeat","angina"], "medium": ["breathless","shortness of breath","high bp","hypertension","swollen legs","dizziness"], "low": ["heart","bp","pulse"]},
    "Orthopedic":         {"high": ["fracture","broken bone","slip disc","sciatica","ligament tear"], "medium": ["joint pain","knee pain","back pain","spine","shoulder pain","neck pain","arthritis"], "low": ["knee","bone","joint","back"]},
    "Ophthalmologist":    {"high": ["vision loss","eye infection","cataract","glaucoma","conjunctivitis"], "medium": ["blurred vision","eye pain","redness in eye","itchy eyes","watery eyes"], "low": ["eye","vision","blur"]},
    "Dentist":            {"high": ["tooth pain","toothache","tooth decay","root canal","broken tooth"], "medium": ["gum pain","gum bleeding","swollen gum","mouth ulcer","cavity"], "low": ["tooth","teeth","gum","dental"]},
    "Dermatologist":      {"high": ["skin rash","eczema","psoriasis","fungal infection","ringworm","hives"], "medium": ["acne","pimples","itching","dry skin","hair loss","dandruff"], "low": ["skin","rash","itch"]},
    "Neurologist":        {"high": ["seizure","epilepsy","stroke","paralysis","severe migraine"], "medium": ["migraine","numbness","tingling","memory loss","tremor","dizziness"], "low": ["headache","brain","nerve"]},
    "Gastroenterologist": {"high": ["severe stomach pain","blood in stool","vomiting blood","jaundice"], "medium": ["acid reflux","ibs","bloating","constipation","diarrhea","stomach pain"], "low": ["stomach","digestion","gas"]},
    "Pulmonologist":      {"high": ["asthma attack","copd","pneumonia","tuberculosis","blood in sputum"], "medium": ["breathless","wheezing","chronic cough","chest tightness"], "low": ["cough","breathing","lung"]},
    "Endocrinologist":    {"high": ["diabetic emergency","thyroid storm","adrenal crisis"], "medium": ["diabetes","thyroid","weight gain","weight loss","fatigue","hormone"], "low": ["sugar","insulin","thyroid"]},
    "Psychiatrist":       {"high": ["suicidal thoughts","psychosis","severe depression","panic attack"], "medium": ["anxiety","depression","insomnia","stress","mood swings","phobia"], "low": ["mental","sleep","worry"]},
    "ENT Specialist":     {"high": ["hearing loss","severe ear pain","throat abscess","nasal polyp"], "medium": ["ear pain","sinus","tonsil","runny nose","snoring","vertigo"], "low": ["ear","nose","throat","sinus"]},
}

AVAILABLE_SLOTS: List[str] = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "02:00 PM", "02:30 PM",
    "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
]

EMERGENCY_KEYWORDS: List[str] = [
    "unconscious", "not breathing", "heart attack", "stroke",
    "severe chest pain", "can't breathe", "collapsed", "bleeding heavily",
    "seizure", "overdose", "poisoning",
]


def find_specialist(symptoms: str) -> Dict:
    """Keyword-weighted specialty matching. Returns structured result dict."""
    text = symptoms.lower()
    weights = {"high": 3, "medium": 2, "low": 1}
    scores: Dict[str, int] = {}

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
    info    = SPECIALTY_INFO.get(specialty, SpecialtyInfo("🏥", "", []))

    return {
        "specialty":      specialty,
        "confidence":     confidence,
        "icon":           info.icon,
        "description":    info.description,
        "doctors":        [d.name for d in doctors],
        "doctor_details": [d._asdict() for d in doctors],
    }


def get_all_specialties() -> List[str]:
    return list(DOCTORS.keys())


def get_available_slots(doctor_name: str, booked: Optional[List[str]] = None) -> List[str]:
    booked = booked or []
    return [s for s in AVAILABLE_SLOTS if s not in booked]
