"""Smart Medicine Reminder AI Agent — Gemini powered"""
from __future__ import annotations
import os, json, io
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

_agent_env = Path(__file__).resolve().parent.parent / ".env"
_root_env  = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_agent_env if _agent_env.exists() else _root_env)

_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL    = "gemini-2.0-flash"
_FALLBACK = "I'm having trouble connecting right now. Please consult your doctor or pharmacist for advice."

SYSTEM = """You are MediCare AI, a warm and knowledgeable medicine reminder assistant for elderly patients.
You help with medicine reminders, missed dose guidance, drug interaction warnings, and emergency detection.
Always speak warmly and simply. For ANY emergency symptom respond with: 🚨 Call 108 immediately.
Never diagnose. End every medical answer with: Please consult your doctor for personalised advice."""

def _call(prompt, image=None):
    """Call Gemini API using new google.genai SDK."""
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=_API_KEY)
        if image is not None:
            contents = [types.Part.from_bytes(data=image, mime_type="image/jpeg"), prompt]
        else:
            contents = SYSTEM + "\n\n" + prompt
        resp = client.models.generate_content(model=MODEL, contents=contents)
        return resp.text.strip()
    except Exception:
        return None

def _model():
    """Fallback: return old-SDK model object if new SDK fails."""
    try:
        import google.generativeai as genai_old
        genai_old.configure(api_key=_API_KEY)
        return genai_old.GenerativeModel(MODEL, system_instruction=SYSTEM)
    except Exception:
        return None

def chat(history: list[dict], user_msg: str) -> str:
    prompt = SYSTEM + "\n\n"
    for m in history[-20:]:
        role = "Patient" if m["role"] == "user" else "MediCare AI"
        prompt += f"{role}: {m['content']}\n"
    prompt += f"Patient: {user_msg}\nMediCare AI:"
    result = _call(prompt)
    if result:
        return result
    try:
        m = _model()
        if m:
            gemini_history = [
                {"role": "user" if h["role"] == "user" else "model", "parts": [h["content"]]}
                for h in history[-20:]
            ]
            return m.start_chat(history=gemini_history).send_message(user_msg).text.strip()
    except Exception:
        pass
    return _FALLBACK

def verify_medicine_image(image_bytes: bytes, scheduled_medicine: str, mime_type: str = "image/jpeg") -> str:
    prompt = (
        f"Look at this medicine image. Read the label. Identify the medicine name and dosage. "
        f"Check if it matches '{scheduled_medicine}'. Reply:\n"
        "**Identified:** <name>\n**Match:** ✅ Yes / ❌ No / ⚠️ Uncertain\n**Note:** <advice>"
    )
    result = _call(prompt, image=image_bytes)
    if result:
        return result
    try:
        import PIL.Image
        img = PIL.Image.open(io.BytesIO(image_bytes))
        m = _model()
        if m:
            return m.generate_content([prompt, img]).text.strip()
    except Exception:
        pass
    return "⚠️ Image analysis failed. Please verify manually."

def analyze_missed_dose(patient: str, medicine: str, missed_count: int, reason: str) -> str:
    severity = "high" if missed_count >= 3 else "moderate" if missed_count == 2 else "low"
    prompt = (
        f"Elderly patient '{patient}' missed '{medicine}' {missed_count} time(s) (severity: {severity}). "
        f"Reason: '{reason}'. Give 3 short lines: risk level, whether to take now or skip, "
        "whether to notify doctor. Warm and brief. End: 'Please consult your doctor.'"
    )
    return _call(prompt) or _FALLBACK

def get_voice_reminder_text(patient: str, medicine: str, dosage: str, time: str, food_instruction: str) -> str:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    return f"{greeting}, {patient}! It's {time}. Please take your {medicine} — {dosage}, {food_instruction}. Take care! 💊"

def analyze_prescription_image(image_bytes: bytes) -> dict:
    prompt = (
        "Read this prescription image carefully (may be handwritten or printed). "
        "Return ONLY valid JSON with keys: patient_name, doctor_name, hospital, date, diagnosis, "
        "medicines (list of {name,dosage,frequency,duration,food_instruction,notes}). "
        "Use empty string for missing fields. Return ONLY raw JSON."
    )
    result = _call(prompt, image=image_bytes)
    if result:
        try:
            text = result.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(text)
        except Exception:
            pass
    try:
        import PIL.Image
        img = PIL.Image.open(io.BytesIO(image_bytes))
        m = _model()
        if m:
            resp = m.generate_content([prompt, img])
            text = resp.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(text)
    except Exception:
        pass
    return {"error": "Could not read the prescription. Please upload a clearer image."}

def explain_prescription_ai(data: dict) -> str:
    meds = data.get("medicines", [])
    if not meds:
        return "No medicines found. Please check the image or enter details manually."
    med_lines = "\n".join(
        f"- {m.get('name','')} {m.get('dosage','')}: {m.get('frequency','')} for {m.get('duration','')} — {m.get('food_instruction','')}"
        for m in meds
    )
    prompt = (
        f"Explain this prescription simply for an elderly patient.\n"
        f"Patient: {data.get('patient_name','')}\nDiagnosis: {data.get('diagnosis','')}\n"
        f"Medicines:\n{med_lines}\n"
        "For each: what it does, how to take it, one precaution. Warm tone. Under 200 words."
    )
    return _call(prompt) or _FALLBACK
