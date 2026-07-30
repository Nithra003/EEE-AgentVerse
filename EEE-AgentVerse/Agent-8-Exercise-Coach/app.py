"""Exercise Coach Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
from exercise_data import CONDITIONS, FITNESS_LEVELS, WEEKLY_SCHEDULE, get_exercise_plan
from utils import generate_report_text
from gemini_helper import ask_gemini
from shared.agent_bridge import get_health_report_events, get_mood_events
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Exercise Coach Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="exercise")
agent_header(
    title="🏃 Exercise Coach Agent",
    subtitle="ElderCare AI — Safe, personalized exercise plans for elderly patients",
    accent="#60a5fa",
)

if "exercise_history" not in st.session_state:
    st.session_state.exercise_history = []

# ── Incoming events from Health Report Agent ───────────────────────────────────
_hr_events = get_health_report_events("Agent-8-Exercise-Coach")
if _hr_events:
    _ev = _hr_events[-1]
    _p  = _ev["payload"]
    st.info(
        f"📊 **Health Report received** — {_p.get('patient_name','')}, "
        f"Age {_p.get('age','')}, Condition: {_p.get('condition','')}, "
        f"Risk: {_p.get('risk_level','')} | {_ev['timestamp']}"
    )

# ── Incoming events from Mood Companion Agent ──────────────────────────────────
_mood_events = get_mood_events()
if _mood_events:
    _ev = _mood_events[-1]
    _p  = _ev["payload"]
    _mood_advice = {
        "Tired":      "Low-intensity stretching only today.",
        "Anxious":    "Gentle breathing exercises recommended.",
        "Sad":        "Light walk outdoors can help lift mood.",
        "Frustrated": "Brisk walk to release tension.",
        "Happy":      "Great day for your full exercise routine!",
        "Lonely":     "Group or outdoor activity encouraged.",
    }.get(_p.get("mood", ""), "Adapt intensity to current mood.")
    st.warning(
        f"😊 **Mood update from Mood Companion** — "
        f"{_p.get('patient_name','')} is feeling **{_p.get('mood','')}**. "
        f"Suggestion: {_mood_advice}"
    )

STEPS = [
    ("name",          "What is the patient's name?"),
    ("age",           "What is the patient's age?"),
    ("condition",     f"What is the patient's health condition? Please type one of:\n\n" + "\n".join(f"- {c}" for c in CONDITIONS)),
    ("fitness_level", f"What is the patient's fitness level? Please type one of: {', '.join(FITNESS_LEVELS)}"),
]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
    st.session_state.data = {}
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your Exercise Coach Assistant.\n\nI will create a safe exercise plan for your patient. Let me ask a few questions.\n\n" + STEPS[0][1]
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if not st.session_state.done:
    user_input = st.chat_input("Type your answer here...")

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

        if key == "condition":
            matched = next((c for c in CONDITIONS if c.lower() == user_input.strip().lower()), None)
            if not matched:
                matched = next((c for c in CONDITIONS if user_input.strip().lower() in c.lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": "Please type one of the listed conditions:\n\n" + "\n".join(f"- {c}" for c in CONDITIONS)})
                st.rerun()
            user_input = matched

        if key == "fitness_level":
            matched = next((f for f in FITNESS_LEVELS if f.lower() == user_input.strip().lower()), None)
            if not matched:
                matched = next((f for f in FITNESS_LEVELS if user_input.strip().lower() in f.lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": f"Please type one of: {', '.join(FITNESS_LEVELS)}"})
                st.rerun()
            user_input = matched

        st.session_state.data[key] = user_input.strip()
        st.session_state.step_index += 1

        if st.session_state.step_index < len(STEPS):
            st.session_state.messages.append({"role": "assistant", "content": STEPS[st.session_state.step_index][1]})
        else:
            d = st.session_state.data
            plan = get_exercise_plan(d["condition"])

            ex_lines = "\n".join(
                f"  - {e['name']} | {e.get('duration', e.get('sets',''))} | {e['benefit']}"
                for e in plan["exercises"]
            )
            precaution_lines = "\n".join(f"  - {p}" for p in plan["precautions"])
            schedule_lines   = "\n".join(f"  {day:12}: {task}" for day, task in WEEKLY_SCHEDULE.items())

            ai_advice = ask_gemini(
                f"You are an expert eldercare fitness coach. Give safe, personalised exercise advice for "
                f"{d['name']}, a {d['age']}-year-old with {d['condition']} at {d['fitness_level']} fitness level. "
                f"Provide: 3 specific exercise tips with modifications for their condition, "
                f"1 critical safety reminder, 1 warm-up suggestion, and 1 motivational sentence. "
                f"Keep it under 130 words. Use simple, encouraging language."
            )

            reply = (
                f"Exercise plan generated for {d['name']}.\n\n"
                f"Plan Overview\n"
                f"-------------\n"
                f"Condition  : {d['condition']}\n"
                f"Intensity  : {plan['intensity']}\n"
                f"Duration   : {plan['duration']}\n"
                f"Description: {plan['description']}\n"
                f"Tip        : {plan['tip']}\n\n"
                f"Daily Exercises\n"
                f"---------------\n"
                f"{ex_lines}\n\n"
                f"Weekly Schedule\n"
                f"---------------\n"
                f"{schedule_lines}\n\n"
                f"Safety Precautions\n"
                f"------------------\n"
                f"{precaution_lines}\n\n"
                f"AI Personalized Advice\n"
                f"----------------------\n"
                f"{ai_advice}\n\n"
                "Type NEW to generate another exercise plan."
            )

            st.session_state.exercise_history.append({
                "Patient": d["name"], "Age": d["age"],
                "Condition": d["condition"], "Fitness Level": d["fitness_level"],
                "Intensity": plan["intensity"],
            })

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.done = True
            st.session_state._report_data = dict(
                name=d["name"], age=d["age"], condition=d["condition"],
                fitness_level=d["fitness_level"], plan=plan, schedule=WEEKLY_SCHEDULE
            )

        st.rerun()
else:
    user_input = st.chat_input("Type NEW to start over...")
    if user_input and user_input.strip().upper() == "NEW":
        for key in ["step_index", "data", "messages", "done", "_report_data"]:
            st.session_state.pop(key, None)
        st.rerun()

    if "_report_data" in st.session_state:
        rd = st.session_state._report_data
        st.download_button(
            "Download Exercise Plan",
            data=generate_report_text(rd),
            file_name=f"exercise_plan_{rd['name'].replace(' ','_')}.txt",
            mime="text/plain",
        )

if st.session_state.exercise_history:
    st.markdown("---")
    st.markdown("**Exercise Plan History**")
    st.dataframe(pd.DataFrame(st.session_state.exercise_history), use_container_width=True, hide_index=True)
