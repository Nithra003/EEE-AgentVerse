"""Smart Medicine Reminder AI Agent — Gemini powered"""
from __future__ import annotations
import os, re, base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load from Agent folder first, fallback to root folder
_agent_env = Path(__file__).resolve().parent.parent / ".env"
_root_env  = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_agent_env if _agent_env.exists() else _root_env)
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

MODEL = "gemini-2.0-flash"

SYSTEM = """You are MediCare AI, a warm and intelligent medicine reminder assistant for elderly patients.
You help with:
- Smart reminders and follow-ups
- Missed dose risk analysis
- Drug interaction warnings
- Emergency detection
- Food-based medicine instructions
- General medicine education (always advise consulting a doctor for personal medical advice)

Rules:
- Be warm, simple, and clear — patient is elderly
- For emergencies (dizziness, chest pain, unconscious, severe symptoms), ALWAYS say: "🚨 This sounds urgent. Please contact your caregiver or call emergency services immediately."
- Never prescribe or change dosages
- Always end medical advice with: "Please consult your doctor for personalised advice."
"""

def _model():
    return genai.GenerativeModel(MODEL, system_instruction=SYSTEM)

def chat(history: list[dict], user_msg: str) -> str:
    """Send a message with full history to Gemini and return reply."""
    try:
        gemini_history = []
        for m in history:
            role = "user" if m["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [m["content"]]})
        session = _model().start_chat(history=gemini_history)
        resp = session.send_message(user_msg)
        return resp.text.strip()
    except Exception as e:
        return f"⚠️ AI unavailable: {e}"

def verify_medicine_image(image_bytes: bytes, scheduled_medicine: str, mime_type: str = "image/jpeg") -> str:
    """Use Gemini Vision to identify medicine from photo and verify against schedule."""
    try:
        import PIL.Image
        import io
        img = PIL.Image.open(io.BytesIO(image_bytes))
        prompt = (
            f"Look at this medicine image carefully. Read any text on the label or strip. "
            f"Identify the medicine name, dosage, and type. "
            f"Then check if it matches '{scheduled_medicine}'. "
            "Reply in this exact format:\n"
            "**Identified:** <medicine name and dosage>\n"
            "**Match:** ✅ Yes / ❌ No / ⚠️ Uncertain\n"
            "**Note:** <one line advice>"
        )
        resp = _model().generate_content([prompt, img])
        return resp.text.strip()
    except Exception as e:
        return f"⚠️ Image analysis failed: {e}"

def analyze_missed_dose(patient: str, medicine: str, missed_count: int, reason: str) -> str:
    prompt = (
        f"Patient '{patient}' has missed '{medicine}' {missed_count} time(s). "
        f"Reason given: '{reason}'. "
        "Provide: 1) Risk level 2) Whether to take now or wait 3) Caregiver alert recommendation. "
        "Keep it brief and warm. End with doctor consultation advice."
    )
    try:
        return _model().generate_content(prompt).text.strip()
    except Exception as e:
        return f"⚠️ Analysis unavailable: {e}"

def get_voice_reminder_text(patient: str, medicine: str, dosage: str, time: str, food_instruction: str) -> str:
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    return (
        f"{greeting}, {patient}! It's {time}. "
        f"Please take your {medicine} — {dosage}, {food_instruction}. "
        "Take care! 💊"
    )
