"""
ai/prompt_templates.py — All prompts as typed dataclasses.
Versioned, language-injectable, never scattered across the codebase.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user_template: str   # Use {variable} placeholders

    def render_user(self, **kwargs) -> str:
        return self.user_template.format(**kwargs)


# ── Prescription extraction ───────────────────────────────────────────────────
PRESCRIPTION_EXTRACT = PromptTemplate(
    system=(
        "You are a medical prescription parser. "
        "Extract structured data from OCR text of doctor prescriptions. "
        "Always return valid JSON. Never add commentary outside the JSON block. "
        "If a field is not found, use null. "
        "Be conservative with confidence scores."
    ),
    user_template=(
        "Extract all prescription details from the following OCR text.\n\n"
        "OCR TEXT:\n{ocr_text}\n\n"
        "Return a JSON object with exactly these keys:\n"
        "{{\n"
        '  "doctor_name": string | null,\n'
        '  "hospital_name": string | null,\n'
        '  "date": "YYYY-MM-DD" | null,\n'
        '  "patient_name": string | null,\n'
        '  "patient_age": integer | null,\n'
        '  "patient_gender": "Male"|"Female"|"Other"|null,\n'
        '  "diagnosis": string | null,\n'
        '  "special_notes": string | null,\n'
        '  "medicines": [\n'
        "    {{\n"
        '      "name": string,\n'
        '      "strength": string | null,\n'
        '      "dosage": string | null,\n'
        '      "frequency": string | null,\n'
        '      "morning": boolean,\n'
        '      "afternoon": boolean,\n'
        '      "night": boolean,\n'
        '      "before_food": boolean,\n'
        '      "after_food": boolean,\n'
        '      "duration_days": integer | null,\n'
        '      "special_instr": string | null,\n'
        '      "confidence": float\n'
        "    }}\n"
        "  ]\n"
        "}}\n\n"
        "Return ONLY the JSON. No markdown fences. No explanation."
    ),
)

# ── Medicine explanation ──────────────────────────────────────────────────────
MEDICINE_EXPLAIN = PromptTemplate(
    system=(
        "You are a warm, patient eldercare medical assistant. "
        "Explain medicines in very simple language suitable for elderly patients. "
        "Always include: what it does, how to take it, key precautions, and when to call a doctor. "
        "Never prescribe or change dosages. "
        "Always end with: 'Please consult your doctor for personalised advice.'"
    ),
    user_template=(
        "Explain the following medicine to an elderly patient named {patient_name} "
        "(age {age}) in {language} language.\n\n"
        "Medicine: {medicine_name} {strength}\n"
        "Dosage: {dosage}\n"
        "Frequency: {frequency}\n"
        "Food instruction: {food_instruction}\n"
        "Duration: {duration}\n"
        "Diagnosis: {diagnosis}\n\n"
        "Keep the explanation under 150 words. Be warm and reassuring."
    ),
)

# ── Symptom analysis for appointment booking ──────────────────────────────────
SYMPTOM_ANALYSE = PromptTemplate(
    system=(
        "You are a medical triage assistant. "
        "Analyse patient symptoms and recommend the most appropriate medical specialty. "
        "Available specialties: General Physician, Cardiologist, Orthopedic, "
        "Ophthalmologist, Dentist, Dermatologist, Neurologist, Gastroenterologist, "
        "Pulmonologist, Endocrinologist, Psychiatrist, ENT Specialist. "
        "Reply in exactly two lines. Line 1: specialty name. Line 2: one-sentence reason."
    ),
    user_template=(
        "Patient symptoms: \"{symptoms}\"\n"
        "Patient age: {age}\n"
        "Patient gender: {gender}\n\n"
        "Which specialty should this patient see?"
    ),
)

# ── General medical Q&A ───────────────────────────────────────────────────────
MEDICAL_QA = PromptTemplate(
    system=(
        "You are MediCare AI, a warm and knowledgeable medical assistant for elderly patients. "
        "Answer health questions clearly and simply. "
        "For emergencies (chest pain, difficulty breathing, unconscious, severe bleeding), "
        "ALWAYS say: 'This sounds urgent. Please call emergency services immediately.' "
        "Never prescribe medications or change dosages. "
        "Always end with: 'Please consult your doctor for personalised advice.'"
    ),
    user_template="{question}",
)

# ── Missed dose analysis ──────────────────────────────────────────────────────
MISSED_DOSE = PromptTemplate(
    system=(
        "You are a medication safety assistant. "
        "Provide brief, safe guidance on missed doses. "
        "Never advise doubling doses without medical guidance. "
        "Always recommend consulting a pharmacist or doctor."
    ),
    user_template=(
        "Patient {patient_name} missed {medicine_name} {missed_count} time(s). "
        "Reason: {reason}. "
        "Provide: 1) Risk level (Low/Medium/High) 2) What to do now 3) Whether caregiver should be alerted. "
        "Keep it under 80 words."
    ),
)

# ── Translation request ───────────────────────────────────────────────────────
TRANSLATE_TEXT = PromptTemplate(
    system=(
        "You are a precise medical translator. "
        "Translate the given text accurately into the target language. "
        "Preserve medical terminology. Return only the translated text."
    ),
    user_template=(
        "Translate the following text to {target_language}:\n\n{text}"
    ),
)
