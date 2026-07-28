INTRO_TEXT = (
    "ElderCare AI is a warm and caring voice companion designed to offer friendly conversations, "
    "emotional support, gentle wellness guidance, and daily encouragement for elderly users."
)

GREETING_MESSAGES = [
    "Hello {name}! I am so glad you are here with me today.",
    "Hi {name}! You are not alone, and I am here to keep you company.",
    "Hello {name}! I am your friendly companion, and I am ready to listen.",
]

MOOD_SUPPORT_MESSAGES = {
    "Happy": "It is wonderful to hear that you are feeling bright today. Keep smiling and enjoy the moment.",
    "Normal": "Thank you for checking in. I am here to support you and help you feel comfortable.",
    "Sad": "I am sorry you are feeling sad. A gentle conversation and a little comfort can help.",
    "Anxious": "Take a slow breath with me. You are safe, and we can take this one step at a time.",
    "Tired": "Resting for a moment may help. Let us take things gently and calmly.",
    "Lonely": "You deserve companionship, and I am happy to stay with you for a while.",
}

MOOD_SUGGESTIONS = {
    "Happy": [
        "Keep smiling and enjoy the day.",
        "Stay active and take a short walk if you feel like it.",
    ],
    "Normal": [
        "Take a few moments to breathe slowly.",
        "Enjoy a warm drink and a calm pause.",
    ],
    "Sad": [
        "Talk with a loved one.",
        "Listen to your favorite music.",
        "Take a quiet moment to rest.",
    ],
    "Anxious": [
        "Practice deep breathing for a minute.",
        "Drink a glass of water.",
        "Relax and give yourself a few calm minutes.",
    ],
    "Tired": [
        "Take a short break and rest.",
        "Sip some water and stretch gently.",
    ],
    "Lonely": [
        "Call a family member or friend.",
        "Take a short walk outside.",
        "Read a favorite book or listen to a story.",
    ],
}

MOTIVATIONAL_QUOTES = [
    "Small steps still move you forward. Keep going.",
    "A calm heart is a strong heart.",
    "You are cared for, and you are doing your best.",
    "Even a quiet day can be a meaningful day.",
    "Hope can be found in one gentle moment at a time.",
]


def get_intro_text() -> str:
    """Return the app introduction text."""
    return INTRO_TEXT


def get_industry_notes() -> list[str]:
    """Return future integration ideas for the broader ElderCare AI ecosystem."""
    return [
        "Medicine Reminder Agent: can suggest gentle medication reminders during the conversation.",
        "Appointment Booking Agent: can help schedule medical visits and support check-ins.",
        "Emergency Detection Agent: can flag urgent concerns and recommend immediate support.",
        "Prescription Explainer Agent: can simplify medication instructions in plain language.",
        "Health Monitoring Agent: can track wellness patterns and offer supportive insights.",
        "Family Notification Agent: can notify relatives when the user needs extra comfort.",
        "Diet Planning Agent: can suggest simple meal ideas and hydration nudges.",
        "Exercise Coach Agent: can encourage gentle movement and mobility habits.",
        "Hospital Navigation Agent: can guide users to the right department or location.",
    ]
