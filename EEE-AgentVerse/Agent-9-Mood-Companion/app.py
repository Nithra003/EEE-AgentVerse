"""Mood Companion Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import random
import streamlit as st
import pandas as pd
from datetime import datetime
from gemini_helper import ask_gemini
from shared.agent_bridge import mood_to_exercise
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Mood Companion Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="mood")
agent_header(
    title="😊 Mood Companion Agent",
    subtitle="ElderCare AI — Emotional wellness and daily positivity support",
    accent="#e879f9",
)

MOOD_DATA = {
    "Happy": {
        "message": "That is wonderful! Your positive energy is truly inspiring.",
        "activities": [
            "Listen to your favourite old songs",
            "Call a friend or family member to share your joy",
            "Take a short walk in the garden",
            "Read an inspiring story or book",
            "Write down 3 things you are grateful for today",
        ],
        "affirmation": "You are loved, valued, and bring joy to everyone around you.",
        "tip": "Share your happiness - it multiplies when shared!",
    },
    "Sad": {
        "message": "It is okay to feel sad sometimes. You are not alone.",
        "activities": [
            "Talk to a family member or trusted friend",
            "Listen to soft, calming music",
            "Sit near a window and enjoy natural light",
            "Make yourself a warm cup of tea or milk",
            "Read a comforting book or watch a light movie",
        ],
        "affirmation": "Every storm passes. Brighter days are ahead for you.",
        "tip": "Do not hesitate to reach out to family - they care about you deeply.",
    },
    "Anxious": {
        "message": "Take a deep breath. You are safe and everything will be okay.",
        "activities": [
            "Try 5 minutes of deep breathing (inhale 4s, hold 4s, exhale 4s)",
            "Take a slow, gentle walk indoors",
            "Practice prayer or meditation",
            "Listen to calming nature sounds",
            "Write down what is worrying you - it helps to express it",
        ],
        "affirmation": "You have overcome challenges before. You are stronger than you think.",
        "tip": "Box breathing: Inhale 4 counts, Hold 4, Exhale 4, Hold 4. Repeat 4 times.",
    },
    "Tired": {
        "message": "Rest is important. Your body is telling you to slow down.",
        "activities": [
            "Take a short 20-minute nap",
            "Drink warm milk or herbal tea",
            "Do gentle seated stretches",
            "Sit quietly in fresh air for 10 minutes",
            "Read something light and relaxing",
        ],
        "affirmation": "Rest is not laziness - it is wisdom. Take care of yourself.",
        "tip": "A 20-minute power nap can restore energy without affecting night sleep.",
    },
    "Frustrated": {
        "message": "It is okay to feel frustrated. Let us find a way to feel better.",
        "activities": [
            "Take a brisk walk to release tension",
            "Listen to uplifting or energetic music",
            "Write down your feelings in a journal",
            "Try progressive muscle relaxation",
            "Talk to someone you trust about how you feel",
        ],
        "affirmation": "Your feelings are valid. You have the strength to work through this.",
        "tip": "Count slowly to 10 before reacting. It gives your mind time to calm down.",
    },
    "Lonely": {
        "message": "You matter deeply to the people around you. Let us connect!",
        "activities": [
            "Call a family member or old friend right now",
            "Join a community singing or prayer group",
            "Visit a neighbour for a short chat",
            "Watch a favourite show or movie",
            "Write a letter or message to someone you miss",
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

BREATHING_STEPS = [
    "Sit comfortably and close your eyes.",
    "Inhale slowly through your nose for 4 counts.",
    "Hold your breath for 4 counts.",
    "Exhale slowly through your mouth for 4 counts.",
    "Hold for 4 counts. Repeat 4 times.",
]

if "mood_history" not in st.session_state:
    st.session_state.mood_history = []
if "daily_affirmation" not in st.session_state:
    st.session_state.daily_affirmation = random.choice(DAILY_AFFIRMATIONS)

STEPS = [
    ("name", "What is your name?"),
    ("age",  "How old are you?"),
    ("mood", f"How are you feeling right now? Please type one of:\n\n" + "\n".join(f"- {m}" for m in MOODS)),
    ("note", "Would you like to share anything about how your day is going? (Type SKIP to continue)"),
]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
    st.session_state.data = {}
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            f"Hello! I am your Mood Companion Assistant.\n\n"
            f"Today's affirmation: \"{st.session_state.daily_affirmation}\"\n\n"
            "I am here to support your emotional wellness. Let me check in with you.\n\n" + STEPS[0][1]
        )
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if not st.session_state.done:
    user_input = st.chat_input("Type your response here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        idx = st.session_state.step_index
        key, _ = STEPS[idx]

        if key == "age":
            try:
                v = int(user_input.strip())
                if not (1 <= v <= 120):
                    raise ValueError
            except ValueError:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid age between 1 and 120."})
                st.rerun()

        if key == "mood":
            matched = next((m for m in MOODS if m.lower() == user_input.strip().lower()), None)
            if not matched:
                matched = next((m for m in MOODS if user_input.strip().lower() in m.lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": "Please type one of the mood options:\n\n" + "\n".join(f"- {m}" for m in MOODS)})
                st.rerun()
            user_input = matched

        st.session_state.data[key] = user_input.strip()
        st.session_state.step_index += 1

        if st.session_state.step_index < len(STEPS):
            st.session_state.messages.append({"role": "assistant", "content": STEPS[st.session_state.step_index][1]})
        else:
            d = st.session_state.data
            note = None if d.get("note", "").upper() == "SKIP" else d.get("note", "")
            response = MOOD_DATA[d["mood"]]
            activity_lines = "\n".join(f"  - {a}" for a in response["activities"])

            note_context = f" They shared: '{note}'" if note else ""
            ai_support = ask_gemini(
                f"You are a compassionate eldercare emotional support companion. "
                f"Write a warm, personal support message for {d['name']}, "
                f"a {d['age']}-year-old who is feeling {d['mood']}.{note_context} "
                f"Acknowledge their feeling first, then offer 1 simple comforting activity "
                f"and 1 gentle reminder that they are cared for. "
                f"Keep it under 80 words. Be gentle, empathetic, and uplifting. "
                f"Do not give medical advice."
            )

            breathing = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(BREATHING_STEPS))

            reply = (
                f"Hello {d['name']}! Here is your personalised support.\n\n"
                f"Mood Response\n"
                f"-------------\n"
                f"Mood    : {d['mood']}\n"
                f"Message : {response['message']}\n"
                f"Tip     : {response['tip']}\n\n"
                f"Affirmation\n"
                f"-----------\n"
                f"\"{response['affirmation']}\"\n\n"
                f"Suggested Activities\n"
                f"--------------------\n"
                f"{activity_lines}\n\n"
                f"AI Support Message\n"
                f"------------------\n"
                f"{ai_support}\n\n"
                f"Breathing Exercise - Box Breathing\n"
                f"----------------------------------\n"
                f"{breathing}\n\n"
                "Type NEW for another check-in."
            )

            st.session_state.mood_history.append({
                "Name": d["name"], "Age": d["age"], "Mood": d["mood"],
                "Note": note if note else "-",
                "Time": datetime.now().strftime("%H:%M:%S"),
            })
            mood_to_exercise(d["name"], d["mood"], int(d["age"]))

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.done = True

        st.rerun()
else:
    user_input = st.chat_input("Type NEW to start over...")
    if user_input and user_input.strip().upper() == "NEW":
        for key in ["step_index", "data", "messages", "done"]:
            st.session_state.pop(key, None)
        st.rerun()

if st.session_state.mood_history:
    st.markdown("---")
    st.markdown("**Today's Mood Log**")
    st.dataframe(pd.DataFrame(st.session_state.mood_history), use_container_width=True, hide_index=True)
