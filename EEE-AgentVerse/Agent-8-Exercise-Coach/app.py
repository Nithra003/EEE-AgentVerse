"""Exercise Coach Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
from exercise_data import CONDITIONS, FITNESS_LEVELS, WEEKLY_SCHEDULE, get_exercise_plan
from utils import generate_report_text
from gemini_helper import ask_gemini

st.set_page_config(page_title="Exercise Coach Agent", layout="centered")

st.markdown("""
<style>
    .chat-header {
        background: #1a3c5e;
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .chat-header h2 { margin: 0; font-size: 1.4rem; }
    .chat-header p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }
    .stChatMessage p { font-size: 1rem; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="chat-header">
    <h2>Exercise Coach Agent</h2>
    <p>ElderCare AI - I will create a safe, personalized exercise plan for your patient.</p>
</div>
""", unsafe_allow_html=True)

if "exercise_history" not in st.session_state:
    st.session_state.exercise_history = []

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
                st.session_state.messages.append({"role": "assistant", "content": "Please type one of the listed conditions:\n\n" + "\n".join(f"- {c}" for c in CONDITIONS)})
                st.rerun()
            user_input = matched

        if key == "fitness_level":
            matched = next((f for f in FITNESS_LEVELS if f.lower() == user_input.strip().lower()), None)
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
            schedule_lines = "\n".join(f"  {day:12}: {task}" for day, task in WEEKLY_SCHEDULE.items())

            ai_advice = ask_gemini(
                f"You are an eldercare fitness coach. Give personalized exercise advice for a {d['age']}-year-old "
                f"named {d['name']} with {d['condition']} at {d['fitness_level']} fitness level. "
                f"Give 3 specific exercise tips, 1 safety reminder, and 1 motivational line. Keep it under 120 words. Be encouraging."
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
