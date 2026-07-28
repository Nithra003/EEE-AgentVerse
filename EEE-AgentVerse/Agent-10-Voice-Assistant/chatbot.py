import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import random
from responses import GREETING_MESSAGES, MOOD_SUPPORT_MESSAGES, MOTIVATIONAL_QUOTES, MOOD_SUGGESTIONS
from gemini_helper import ask_gemini


def _normalize_message(user_message: str) -> str:
    return (user_message or "").strip().lower()


def generate_ai_response(patient_name: str, user_message: str, mood: str) -> str:
    """Generate AI response using Gemini with fallback to rule-based."""
    name = (patient_name or "friend").strip()
    prompt = (
        f"You are a warm, caring eldercare voice companion. "
        f"The patient's name is {name}, age-related context: elderly, current mood: {mood}. "
        f"They said: '{user_message}'. "
        f"Respond with empathy, warmth, and encouragement. Keep it under 80 words. "
        f"Do not give medical advice. Be conversational and kind."
    )
    ai_response = ask_gemini(prompt)
    if ai_response and "Unable to generate" not in ai_response:
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
