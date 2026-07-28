"""Demo data loader for hackathon judges."""
from medicine_db import log_dose

def load_demo(patient: str = "Rajan"):
    entries = [
        (patient, "Metformin",  "taken",   ""),
        (patient, "Amlodipine", "taken",   ""),
        (patient, "Vitamin D",  "missed",  "Forgot after lunch"),
        (patient, "Omeprazole", "taken",   ""),
        (patient, "Metformin",  "taken",   ""),
        (patient, "Amlodipine", "missed",  "Was travelling"),
        (patient, "Vitamin D",  "taken",   ""),
        (patient, "Omeprazole", "taken",   ""),
        (patient, "Metformin",  "taken",   ""),
        (patient, "Amlodipine", "taken",   ""),
    ]
    for p, m, s, n in entries:
        log_dose(p, m, s, n)
