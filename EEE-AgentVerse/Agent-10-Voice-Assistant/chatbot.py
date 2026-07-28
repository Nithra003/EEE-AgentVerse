import random

from responses import (
    GREETING_MESSAGES,
    MOOD_SUPPORT_MESSAGES,
    MOTIVATIONAL_QUOTES,
    MOOD_SUGGESTIONS,
)


def _normalize_message(user_message: str) -> str:
    """Normalize user input for simple intent detection."""
    return (user_message or "").strip().lower()


def generate_ai_response(patient_name: str, user_message: str, mood: str) -> str:
    """Generate a friendly and supportive AI response."""
    name = (patient_name or "friend").strip()
    normalized_message = _normalize_message(user_message)

    parts = []
    parts.append(random.choice(GREETING_MESSAGES).format(name=name))

    if any(keyword in normalized_message for keyword in ["hello", "hi", "hey"]):
        parts.append("It is lovely to hear from you today.")

    if any(
        keyword in normalized_message
        for keyword in ["feel", "feeling", "sad", "lonely", "tired", "anxious", "happy", "worried", "upset"]
    ):
        parts.append("Thank you for sharing that with me. I am here to listen and support you.")

    if mood:
        parts.append(MOOD_SUPPORT_MESSAGES.get(mood, MOOD_SUPPORT_MESSAGES["Normal"]))

    parts.append("Would you like to talk for a while, hear a cheerful thought, or take a calming breath with me?")

    if any(keyword in normalized_message for keyword in ["water", "drink"]):
        parts.append("A small sip of water can help you feel refreshed.")
    if any(keyword in normalized_message for keyword in ["break", "rest"]):
        parts.append("A short rest can do wonders for your energy.")
    if any(keyword in normalized_message for keyword in ["family", "friend", "loved"]):
        parts.append("Reaching out to a loved one could bring comfort and warmth.")

    return " ".join(parts)


def get_wellness_suggestions(mood: str) -> list[str]:
    """Return tailored wellness suggestions based on mood."""
    return MOOD_SUGGESTIONS.get(mood, MOOD_SUGGESTIONS["Normal"])


def get_daily_motivation() -> str:
    """Return a random motivational quote."""
    return random.choice(MOTIVATIONAL_QUOTES)
