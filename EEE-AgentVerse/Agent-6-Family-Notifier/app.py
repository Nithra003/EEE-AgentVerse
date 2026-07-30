"""Family Notification Agent - AI Assistant Style"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import pandas as pd
from utils import EMERGENCY_TYPES, RELATIONSHIP_OPTIONS, validate_fields, generate_report_text
from notifications import build_notification, simulate_notification_channels, add_to_history
from gemini_helper import ask_gemini
from shared.agent_bridge import get_emergency_events
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Family Notification Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="family")
agent_header(
    title="👨‍👩‍👧 Family Notification Agent",
    subtitle="ElderCare AI — Instant emergency alerts to family members",
    accent="#fb923c",
)

if "history" not in st.session_state:
    st.session_state.history = []

# ── Incoming events from Emergency Detection Agent ─────────────────────────────
_em_events = get_emergency_events()
if _em_events:
    for _ev in _em_events:
        _p = _ev["payload"]
        st.error(
            f"🚨 **Auto-alert from Emergency Detection Agent** — "
            f"{_p.get('patient_name','Unknown')} | {_p.get('status','Fall Detected')} | "
            f"Location: {_p.get('location','Unknown')} | Risk: {_p.get('risk_level','HIGH')} | "
            f"{_ev['timestamp']}"
        )

STEPS = [
    ("patient_name",    "What is the patient's name?"),
    ("age",             "What is the patient's age?"),
    ("location",        "What is the patient's current location? For example: 12, Anna Nagar, Chennai."),
    ("emergency_type",  f"What type of emergency is this? Please type one of the following:\n\n" + "\n".join(f"- {e}" for e in EMERGENCY_TYPES)),
    ("contact_name",    "What is the emergency contact person's name?"),
    ("relationship",    f"What is their relationship to the patient? Options: {', '.join(RELATIONSHIP_OPTIONS)}"),
    ("contact_number",  "What is the contact person's 10-digit mobile number?"),
]

if "step_index" not in st.session_state:
    st.session_state.step_index = 0
    st.session_state.data = {}
    st.session_state.messages = []
    st.session_state.done = False
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I am your Family Notification Assistant.\n\nI will help you send an emergency alert to the patient's family. Let me ask you a few questions.\n\n" + STEPS[0][1]
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
                age_val = int(user_input.strip())
                if not (1 <= age_val <= 120):
                    st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid age between 1 and 120."})
                    st.rerun()
            except ValueError:
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid age number."})
                st.rerun()

        if key == "emergency_type":
            matched = next((e for e in EMERGENCY_TYPES if e.lower() == user_input.strip().lower()), None)
            if not matched:
                matched = next((e for e in EMERGENCY_TYPES if user_input.strip().lower() in e.lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": f"Please type one of the valid emergency types:\n\n" + "\n".join(f"- {e}" for e in EMERGENCY_TYPES)})
                st.rerun()
            user_input = matched

        if key == "relationship":
            matched = next((r for r in RELATIONSHIP_OPTIONS if r.lower() == user_input.strip().lower()), None)
            if not matched:
                matched = next((r for r in RELATIONSHIP_OPTIONS if user_input.strip().lower() in r.lower()), None)
            if not matched:
                st.session_state.messages.append({"role": "assistant", "content": f"Please type one of: {', '.join(RELATIONSHIP_OPTIONS)}"})
                st.rerun()
            user_input = matched

        if key == "contact_number":
            import re
            if not re.fullmatch(r"\d{10}", user_input.strip()):
                st.session_state.messages.append({"role": "assistant", "content": "Please enter a valid 10-digit mobile number."})
                st.rerun()

        st.session_state.data[key] = user_input.strip()
        st.session_state.step_index += 1

        if st.session_state.step_index < len(STEPS):
            st.session_state.messages.append({"role": "assistant", "content": STEPS[st.session_state.step_index][1]})
        else:
            d = st.session_state.data
            notification = build_notification(
                d["patient_name"], int(d["age"]), d["emergency_type"],
                d["location"], d["contact_name"], d["relationship"], d["contact_number"]
            )
            st.session_state.history = add_to_history(st.session_state.history, notification)

            channels = simulate_notification_channels(notification["priority"])
            channel_lines = "\n".join(f"- {msg}" for _, msg, _ in channels)

            ai_msg = ask_gemini(
                f"You are an eldercare emergency notification AI. Write a concise, calm, and urgent "
                f"notification message for a family member. "
                f"Patient: {d['patient_name']}, Age: {d['age']}, Emergency: {d['emergency_type']}, "
                f"Location: {d['location']}. Contact: {d['contact_name']} ({d['relationship']}). "
                f"Priority: {notification['priority']}. "
                f"Include: what happened, where, and what the family member should do next. "
                f"Keep it under 60 words. Be clear, calm, and compassionate."
            )

            reply = (
                f"Emergency notification sent successfully.\n\n"
                f"Notification Summary\n"
                f"--------------------\n"
                f"Patient        : {notification['patient_name']}\n"
                f"Age            : {notification['age']}\n"
                f"Emergency      : {notification['emergency_type']}\n"
                f"Priority       : {notification['priority']}\n"
                f"Location       : {notification['location']}\n"
                f"Contact Person : {notification['contact_name']} ({notification['relationship']})\n"
                f"Contact Number : {notification['contact_number']}\n"
                f"Date and Time  : {notification['date']} at {notification['time']}\n"
                f"Status         : {notification['status']}\n\n"
                f"Notification Channels\n"
                f"---------------------\n"
                f"{channel_lines}\n\n"
                f"AI Generated Message\n"
                f"--------------------\n"
                f"{ai_msg}\n\n"
                "Type NEW to send another notification."
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.done = True
            st.session_state._notification = notification

        st.rerun()
else:
    user_input = st.chat_input("Type NEW to start over...")
    if user_input and user_input.strip().upper() == "NEW":
        for key in ["step_index", "data", "messages", "done", "_notification"]:
            st.session_state.pop(key, None)
        st.rerun()

    if "_notification" in st.session_state:
        report_text = generate_report_text(st.session_state._notification)
        n = st.session_state._notification
        st.download_button(
            "Download Emergency Report",
            data=report_text,
            file_name=f"emergency_report_{n['date']}_{n['time'].replace(':', '-')}.txt",
            mime="text/plain",
        )

if st.session_state.history:
    st.markdown("---")
    st.markdown("**Notification History**")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
