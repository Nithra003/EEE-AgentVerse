import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import random
from responses import GREETING_MESSAGES, MOOD_SUPPORT_MESSAGES, MOTIVATIONAL_QUOTES, MOOD_SUGGESTIONS
from gemini_helper import ask_gemini


def _normalize_message(user_message: str) -> str:
    return (user_message or "").strip().lower()


def generate_ai_response(patient_name: str, user_message: str, mood: str) -> str:
    """Generate AI response using Gemini with rule-based fallback."""
    name = (patient_name or "friend").strip()
    msg  = (user_message or "").strip()
    if not msg:
        return f"I'm here with you, {name}. Feel free to share anything on your mind."

    prompt = (
        f"You are a warm, patient eldercare voice companion named Companion. "
        f"The patient's name is {name} (elderly). Current mood: {mood}. "
        f"They said: '{msg}'. "
        f"Respond with genuine empathy and warmth. "
        f"If they mention pain, discomfort, or a health concern, gently suggest they speak to their doctor or caregiver. "
        f"Do not give medical advice. Keep response under 80 words. Be conversational and kind."
    )
    ai_response = ask_gemini(prompt)
    if ai_response and "unavailable" not in ai_response.lower() and "Unable" not in ai_response:
        return ai_response
    # Fallback
    parts = [random.choice(GREETING_MESSAGES).format(name=name)]
    if mood:
        parts.append(MOOD_SUPPORT_MESSAGES.get(mood, MOOD_SUPPORT_MESSAGES["Normal"]))
    parts.append("Would you like to talk for a while or hear a cheerful thought?")
    return " ".join(parts)


def get_wellness_suggestions(mood: str) -> list[str]:
    """Return tailored wellness suggestions based on mood."""
    return MOOD_SUGGESTIONS.get(mood, MOOD_SUGGESTIONS["Normal"])


def get_daily_motivation() -> str:
    """Return a random motivational quote."""
    return random.choice(MOTIVATIONAL_QUOTES)
