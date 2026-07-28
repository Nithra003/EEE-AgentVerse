"""Diet Recommendation Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
from diet_data import CONDITIONS, calculate_bmi, get_diet_plan
from utils import generate_report_text
from gemini_helper import ask_gemini

st.set_page_config(page_title="Diet Recommendation Agent", layout="centered")

st.markdown("""
<style>
    .chat-header {
        background: #1e5631;
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
    <h2>Diet Recommendation Agent</h2>
    <p>ElderCare AI - I will create a personalized diet plan based on your health condition.</p>
</div>
""", unsafe_allow_html=True)

if "diet_history" not in st.session_state:
    st.session_state.diet_history = []

STEPS = [
    ("name",      "What is the patient's name?"),
    ("age",       "What is the patient's age?"),
    ("gender",    "What is the patient's gender? Please type: Male, Female, or Other."),
    ("weight",    "What is the patient's weight in kg? For example: 70"),
    ("height",    "What is the patient's height in cm? For example: 165"),
    ("condition", f"What is the patient's health condition? Please type one of:\n\n" + "\n".join(f"- {c}" for c in CONDITIONS)),
]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
    st.session_state.data = {}
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your Diet Recommendation Assistant.\n\nI will create a personalized diet plan for your patient. Let me ask a few questions.\n\n" + STEPS[0][1]
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

        # Validations
        if key == "age":
            try:
                v = int(user_input.strip())
                if not (1 <= v <= 120):
                    raise ValueError
            except ValueError:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid age between 1 and 120."})
                st.rerun()

        if key == "gender":
            if user_input.strip().lower() not in ["male", "female", "other"]:
                st.session_state.messages.append({"role": "assistant", "content": "Please type Male, Female, or Other."})
                st.rerun()
            user_input = user_input.strip().title()

        if key == "weight":
            try:
                v = float(user_input.strip())
                if not (20 <= v <= 300):
                    raise ValueError
            except ValueError:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid weight between 20 and 300 kg."})
                st.rerun()

        if key == "height":
            try:
                v = float(user_input.strip())
                if not (50 <= v <= 250):
                    raise ValueError
            except ValueError:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid height between 50 and 250 cm."})
                st.rerun()

        if key == "condition":
            matched = next((c for c in CONDITIONS if c.lower() == user_input.strip().lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": "Please type one of the listed conditions:\n\n" + "\n".join(f"- {c}" for c in CONDITIONS)})
                st.rerun()
            user_input = matched

        st.session_state.data[key] = user_input.strip()
        st.session_state.step_index += 1

        if st.session_state.step_index < len(STEPS):
            st.session_state.messages.append({"role": "assistant", "content": STEPS[st.session_state.step_index][1]})
        else:
            d = st.session_state.data
            bmi, bmi_cat = calculate_bmi(float(d["weight"]), float(d["height"]))
            plan = get_diet_plan(d["condition"])

            meal_lines = "\n".join(f"  {k:15}: {v}" for k, v in plan["meal_plan"].items())
            eat_lines  = "\n".join(f"  - {f}" for f in plan["foods_to_eat"])
            avoid_lines = "\n".join(f"  - {f}" for f in plan["foods_to_avoid"])

            ai_advice = ask_gemini(
                f"You are an eldercare nutritionist. Give personalized diet advice for a {d['age']}-year-old "
                f"{d['gender']} named {d['name']} with {d['condition']}. BMI: {bmi} ({bmi_cat}), "
                f"Weight: {d['weight']}kg, Height: {d['height']}cm. "
                f"Give 3 specific food tips, 1 meal timing tip, and 1 motivational line. Keep it under 120 words. Be warm."
            )

            reply = (
                f"Diet plan generated for {d['name']}.\n\n"
                f"BMI Analysis\n"
                f"------------\n"
                f"BMI Score  : {bmi}\n"
                f"Category   : {bmi_cat}\n"
                f"Condition  : {d['condition']}\n\n"
                f"Diet Plan\n"
                f"---------\n"
                f"{plan['description']}\n"
                f"Water Intake : {plan['water_intake']}\n"
                f"Tip          : {plan['tip']}\n\n"
                f"Daily Meal Schedule\n"
                f"-------------------\n"
                f"{meal_lines}\n\n"
                f"Foods to Eat\n"
                f"------------\n"
                f"{eat_lines}\n\n"
                f"Foods to Avoid\n"
                f"--------------\n"
                f"{avoid_lines}\n\n"
                f"AI Personalized Advice\n"
                f"----------------------\n"
                f"{ai_advice}\n\n"
                "Type NEW to generate another diet plan."
            )

            st.session_state.diet_history.append({
                "Patient": d["name"], "Age": d["age"],
                "Condition": d["condition"], "BMI": bmi, "Category": bmi_cat,
            })

            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.done = True
            st.session_state._report_data = dict(
                name=d["name"], age=d["age"], gender=d["gender"],
                weight=float(d["weight"]), height=float(d["height"]),
                bmi=bmi, bmi_category=bmi_cat, condition=d["condition"], plan=plan
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
            "Download Diet Report",
            data=generate_report_text(rd),
            file_name=f"diet_report_{rd['name'].replace(' ','_')}.txt",
            mime="text/plain",
        )

if st.session_state.diet_history:
    st.markdown("---")
    st.markdown("**Diet Plan History**")
    st.dataframe(pd.DataFrame(st.session_state.diet_history), use_container_width=True, hide_index=True)
