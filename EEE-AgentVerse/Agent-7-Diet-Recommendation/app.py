"""Diet Recommendation Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from diet_data import CONDITIONS, calculate_bmi, get_diet_plan
from utils import generate_report_text
from gemini_helper import ask_gemini
from shared.agent_bridge import get_health_report_events
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Diet Recommendation Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="diet")
agent_header(
    title="🥗 Diet Recommendation Agent",
    subtitle="ElderCare AI — Personalized diet plans based on your health condition",
    accent="#4ade80",
)

if "diet_history" not in st.session_state:
    st.session_state.diet_history = []

# ── Incoming events from Health Report Agent ───────────────────────────────────
_hr_events = get_health_report_events("Agent-7-Diet-Recommendation")
if _hr_events:
    _ev = _hr_events[-1]
    _p  = _ev["payload"]
    st.info(
        f"📊 **Health Report received** — {_p.get('patient_name','')}, "
        f"Age {_p.get('age','')}, Condition: {_p.get('condition','')}, "
        f"Risk: {_p.get('risk_level','')} | {_ev['timestamp']}\n\n"
        f"Recommendations: {'; '.join(_p.get('recommendations', []))}"
    )

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
                matched = next((c for c in CONDITIONS if user_input.strip().lower() in c.lower()), None)
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

            meal_lines  = "\n".join(f"  {k:15}: {v}" for k, v in plan["meal_plan"].items())
            eat_lines   = "\n".join(f"  - {f}" for f in plan["foods_to_eat"])
            avoid_lines = "\n".join(f"  - {f}" for f in plan["foods_to_avoid"])

            ai_advice = ask_gemini(
                f"You are an expert eldercare nutritionist. Give personalised, practical diet advice for "
                f"{d['name']}, a {d['age']}-year-old {d['gender']} with {d['condition']}. "
                f"BMI: {bmi} ({bmi_cat}), Weight: {d['weight']}kg, Height: {d['height']}cm. "
                f"Provide: 3 specific food recommendations with reasons, 1 meal timing tip, "
                f"1 food to strictly avoid with reason, and 1 warm motivational sentence. "
                f"Keep it under 130 words. Use simple language suitable for an elderly patient."
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

        # ── Auto Pie Chart ────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 🥧 Nutrition Distribution")
        plan = rd["plan"]
        NUTRITION = {
            "Diabetes":           {"Carbohydrates": 40, "Protein": 30, "Healthy Fats": 20, "Fiber": 10},
            "High Blood Pressure":{"Carbohydrates": 45, "Protein": 25, "Healthy Fats": 20, "Fiber": 10},
            "Heart Disease":      {"Carbohydrates": 40, "Protein": 25, "Healthy Fats": 25, "Fiber": 10},
            "Arthritis":          {"Carbohydrates": 40, "Protein": 30, "Healthy Fats": 20, "Fiber": 10},
            "General Wellness":   {"Carbohydrates": 50, "Protein": 20, "Healthy Fats": 20, "Fiber": 10},
        }
        nutrition = NUTRITION.get(rd["condition"], NUTRITION["General Wellness"])
        colors = ["#4f9cf9", "#34d399", "#fbbf24", "#a78bfa"]
        fig = go.Figure(go.Pie(
            labels=list(nutrition.keys()),
            values=list(nutrition.values()),
            hole=0.4,
            marker=dict(colors=colors, line=dict(color="#080d18", width=2)),
            textinfo="label+percent",
            textfont=dict(size=13),
        ))
        fig.update_layout(
            title=dict(text=f"Recommended Nutrition for {rd['condition']}", font=dict(color="#e2eaf5", size=15)),
            paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
            font=dict(color="#e2eaf5"),
            legend=dict(font=dict(color="#8899aa")),
            margin=dict(t=50, b=20, l=20, r=20),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Meal Calories Bar Chart ───────────────────────────────────────────
        MEAL_CALORIES = {
            "Diabetes":           {"Breakfast": 300, "Mid-Morning": 100, "Lunch": 450, "Evening Snack": 150, "Dinner": 400},
            "High Blood Pressure":{"Breakfast": 320, "Mid-Morning": 80,  "Lunch": 480, "Evening Snack": 120, "Dinner": 420},
            "Heart Disease":      {"Breakfast": 280, "Mid-Morning": 120, "Lunch": 440, "Evening Snack": 130, "Dinner": 380},
            "Arthritis":          {"Breakfast": 300, "Mid-Morning": 100, "Lunch": 460, "Evening Snack": 140, "Dinner": 400},
            "General Wellness":   {"Breakfast": 350, "Mid-Morning": 100, "Lunch": 500, "Evening Snack": 150, "Dinner": 450},
        }
        cal = MEAL_CALORIES.get(rd["condition"], MEAL_CALORIES["General Wellness"])
        fig2 = go.Figure(go.Bar(
            x=list(cal.keys()), y=list(cal.values()),
            marker_color=colors,
            text=[f"{v} kcal" for v in cal.values()],
            textposition="outside",
            textfont=dict(color="#e2eaf5"),
        ))
        fig2.update_layout(
            title=dict(text="Estimated Calories per Meal", font=dict(color="#e2eaf5", size=15)),
            paper_bgcolor="#0d1526", plot_bgcolor="#0d1526",
            font=dict(color="#e2eaf5"),
            xaxis=dict(color="#8899aa"), yaxis=dict(color="#8899aa", title="Calories (kcal)"),
            margin=dict(t=50, b=20, l=20, r=20),
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

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
