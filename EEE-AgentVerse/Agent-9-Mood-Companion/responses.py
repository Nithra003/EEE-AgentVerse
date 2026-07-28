"""
responses.py - Mood-based responses and activities for Mood Companion Agent
"""

MOOD_DATA = {
    "😊 Happy": {
        "color": "#1E8449",
        "message": "That's wonderful! Your positive energy is truly inspiring. 😊",
        "activities": [
            "🎵 Listen to your favourite old songs",
            "📞 Call a friend or family member to share your joy",
            "🌿 Take a short walk in the garden",
            "📖 Read an inspiring story or book",
            "✍️ Write down 3 things you are grateful for today",
        ],
        "affirmation": "You are loved, valued, and bring joy to everyone around you.",
        "tip": "Share your happiness – it multiplies when shared!",
    },
    "😔 Sad": {
        "color": "#2874A6",
        "message": "It's okay to feel sad sometimes. You are not alone. 💙",
        "activities": [
            "🫂 Talk to a family member or trusted friend",
            "🎵 Listen to soft, calming music",
            "🌸 Sit near a window and enjoy natural light",
            "🍵 Make yourself a warm cup of tea or milk",
            "📖 Read a comforting book or watch a light movie",
        ],
        "affirmation": "Every storm passes. Brighter days are ahead for you.",
        "tip": "Don't hesitate to reach out to family – they care about you deeply.",
    },
    "😰 Anxious": {
        "color": "#7D6608",
        "message": "Take a deep breath. You are safe and everything will be okay. 🌿",
        "activities": [
            "🧘 Try 5 minutes of deep breathing (inhale 4s, hold 4s, exhale 4s)",
            "🚶 Take a slow, gentle walk indoors",
            "📿 Practice prayer or meditation",
            "🎵 Listen to calming nature sounds",
            "✍️ Write down what is worrying you – it helps to express it",
        ],
        "affirmation": "You have overcome challenges before. You are stronger than you think.",
        "tip": "Box breathing: Inhale 4 counts → Hold 4 → Exhale 4 → Hold 4. Repeat 4 times.",
    },
    "😴 Tired": {
        "color": "#6C3483",
        "message": "Rest is important. Your body is telling you to slow down. 💜",
        "activities": [
            "😴 Take a short 20-minute nap",
            "🍵 Drink warm milk or herbal tea",
            "🧘 Do gentle seated stretches",
            "🌿 Sit quietly in fresh air for 10 minutes",
            "📖 Read something light and relaxing",
        ],
        "affirmation": "Rest is not laziness – it is wisdom. Take care of yourself.",
        "tip": "A 20-minute power nap can restore energy without affecting night sleep.",
    },
    "😠 Frustrated": {
        "color": "#C0392B",
        "message": "It's okay to feel frustrated. Let's find a way to feel better. ❤️",
        "activities": [
            "🚶 Take a brisk walk to release tension",
            "🎵 Listen to uplifting or energetic music",
            "✍️ Write down your feelings in a journal",
            "🧘 Try progressive muscle relaxation",
            "📞 Talk to someone you trust about how you feel",
        ],
        "affirmation": "Your feelings are valid. You have the strength to work through this.",
        "tip": "Count slowly to 10 before reacting. It gives your mind time to calm down.",
    },
    "😐 Lonely": {
        "color": "#117A65",
        "message": "You matter deeply to the people around you. Let's connect! 🌟",
        "activities": [
            "📞 Call a family member or old friend right now",
            "🎵 Join a community singing or prayer group",
            "🌿 Visit a neighbour for a short chat",
            "📺 Watch a favourite show or movie",
            "✍️ Write a letter or message to someone you miss",
        ],
        "affirmation": "You are never truly alone. People love and think about you.",
        "tip": "Even a 5-minute phone call can brighten your day and someone else's too.",
    },
}

MOODS = list(MOOD_DATA.keys())

DAILY_AFFIRMATIONS = [
    "Every day is a new opportunity to feel better.",
    "You are stronger than you know.",
    "Small steps forward are still progress.",
    "You are loved and appreciated.",
    "Your smile makes the world brighter.",
    "Today is a good day to be alive.",
    "You have wisdom that only comes with experience.",
]

BREATHING_EXERCISE = {
    "name": "Box Breathing",
    "steps": [
        "Sit comfortably and close your eyes.",
        "Inhale slowly through your nose for 4 counts.",
        "Hold your breath for 4 counts.",
        "Exhale slowly through your mouth for 4 counts.",
        "Hold for 4 counts. Repeat 4 times.",
    ],
    "benefit": "Reduces anxiety and calms the nervous system in under 2 minutes.",
}


def get_mood_response(mood: str) -> dict:
    return MOOD_DATA.get(mood, MOOD_DATA["😊 Happy"])
