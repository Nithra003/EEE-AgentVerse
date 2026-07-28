"""Prescription Explainer Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
from medicine_data import MedicineKnowledgeBase
from utils import build_summary_text
from gemini_helper import ask_gemini

st.set_page_config(page_title="Prescription Explainer Agent", layout="centered")

st.markdown("""
<style>
    .chat-header {
        background: #0f766e;
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
    <h2>Prescription Explainer Agent</h2>
    <p>ElderCare AI - I will explain your prescription in simple, easy-to-understand language.</p>
</div>
""", unsafe_allow_html=True)

STEPS = [
    ("patient_name",      "What is the patient's name?"),
    ("age",               "How old is the patient?"),
    ("medicine_name",     "What is the name of the medicine?"),
    ("dosage",            "What is the dosage? For example: 500 mg, 1 tablet."),
    ("frequency",         "How often should it be taken? For example: twice daily, once at night."),
    ("food_relation",     "Should it be taken before food, after food, with food, or any time?"),
    ("duration",          "For how many days should the patient take this medicine?"),
    ("medical_condition", "What medical condition is this medicine prescribed for?"),
]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
    st.session_state.data = {}
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your Prescription Explainer Assistant.\n\nI will help explain this prescription in simple language. Let me ask you a few questions.\n\n" + STEPS[0][1]
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
        st.session_state.data[key] = user_input.strip()
        st.session_state.step_index += 1

        if st.session_state.step_index < len(STEPS):
            next_question = STEPS[st.session_state.step_index][1]
            st.session_state.messages.append({"role": "assistant", "content": next_question})
        else:
            d = st.session_state.data
            kb = MedicineKnowledgeBase()
            medicine = kb.get_medicine(d["medicine_name"]) or kb.get_generic_medicine(d["medicine_name"])

            info = (
                f"Prescription Details\n"
                f"--------------------\n"
                f"Patient          : {d['patient_name']}\n"
                f"Age              : {d['age']}\n"
                f"Medicine         : {medicine.name}\n"
                f"Purpose          : {medicine.purpose}\n"
                f"Treats           : {medicine.treats}\n"
                f"How to take      : {medicine.how_to_take.format(dosage=d['dosage'], frequency=d['frequency'])}\n"
                f"Best time        : {medicine.best_time}\n"
                f"Food relation    : {d['food_relation']}\n"
                f"Duration         : {d['duration']} days\n"
                f"Missed dose      : {medicine.missed_dose}\n\n"
                f"Precautions\n"
                f"-----------\n" +
                "\n".join(f"- {p}" for p in medicine.precautions) +
                "\n\nSide Effects\n"
                f"------------\n" +
                "\n".join(f"- {s}" for s in medicine.side_effects)
            )

            ai_prompt = (
                f"You are a friendly eldercare assistant. Explain the medicine '{d['medicine_name']}' "
                f"prescribed for '{d['medical_condition']}' to a {d['age']}-year-old patient named {d['patient_name']}. "
                f"Dosage: {d['dosage']}, Frequency: {d['frequency']}, Duration: {d['duration']} days, {d['food_relation']}. "
                f"Use very simple language. Include: what it does, how to take it, 2 precautions, 1 tip. "
                f"Keep it under 150 words. Be warm and reassuring."
            )
            ai_response = ask_gemini(ai_prompt)

            summary = build_summary_text(
                patient_name=d["patient_name"],
                medicine_name=medicine.name,
                dosage=d["dosage"],
                frequency=d["frequency"],
                duration=d["duration"],
                purpose=medicine.purpose,
            )

            reply = (
                f"{info}\n\n"
                f"AI Explanation\n"
                f"--------------\n"
                f"{ai_response}\n\n"
                "Type NEW to explain another prescription."
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.done = True
            st.session_state._summary = summary
            st.session_state._patient = d["patient_name"]

        st.rerun()
else:
    user_input = st.chat_input("Type NEW to start over...")
    if user_input and user_input.strip().upper() == "NEW":
        for key in ["step_index", "data", "messages", "done", "_summary", "_patient"]:
            st.session_state.pop(key, None)
        st.rerun()

    if hasattr(st.session_state, "_summary") or "_summary" in st.session_state:
        st.download_button(
            label="Download Prescription Summary",
            data=st.session_state._summary.encode("utf-8"),
            file_name=f"{st.session_state.get('_patient','patient').replace(' ','_').lower()}_summary.txt",
            mime="text/plain",
        )
