# app.py - ElderCare AI Agent - Appointment Booking

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
from agent import AppointmentAgent
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Appointment Booking Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="appointment")
agent_header(
    title="📅 Appointment Booking Agent",
    subtitle="ElderCare AI — Book doctor appointments step by step",
    accent="#34d399",
)

# Sidebar extra info
with st.sidebar:
    st.markdown("---")
    api_key = st.text_input(
        "Gemini API Key (Optional)",
        type="password",
        placeholder="Paste your API key here",
        help="Free key: https://aistudio.google.com/app/apikey",
    )
    st.caption("Used only for AI symptom analysis. Never stored.")
    if st.button("Start Over", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    if "agent" in st.session_state:
        a = st.session_state.agent
        st.caption(f"Step: {a.state}")
        if a.patient.get("name"):
            st.caption(f"Patient: {a.patient['name']}")
        if a.specialty:
            st.caption(f"Specialty: {a.specialty}")

# Init agent
if "agent" not in st.session_state:
    st.session_state.agent    = AppointmentAgent(api_key or "")
    st.session_state.messages = []
    first = st.session_state.agent.process("start")
    st.session_state.messages.append({
        "role": "agent", "content": first["message"], "data": first
    })

# Update API key if entered after load
if api_key and st.session_state.agent.api_key != api_key:
    try:
        import google.generativeai as genai
        st.session_state.agent.api_key = api_key
        genai.configure(api_key=api_key)
        st.session_state.agent.model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        st.session_state.agent.api_key = api_key

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "agent":
        with st.chat_message("assistant"):
            data = msg.get("data", {})
            if data.get("emergency"):
                st.markdown(
                    f'<div class="emergency-box">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(msg["content"])

            dl = data.get("data", {}).get("download")
            if dl:
                st.download_button(
                    "Download Appointment Confirmation",
                    data=dl,
                    file_name=data["data"]["filename"],
                    mime="text/plain",
                    key=f"dl_{id(msg)}",
                    use_container_width=True,
                )
    else:
        with st.chat_message("user"):
            st.markdown(msg["content"])

# Voice input
def record_voice() -> str:
    try:
        import speech_recognition as sr
        r   = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=6, phrase_time_limit=10)
        try:
            return r.recognize_google(audio, language="ta-IN")
        except Exception:
            return r.recognize_google(audio, language="en-IN")
    except Exception:
        return ""

agent = st.session_state.agent

col1, col2 = st.columns([1, 6])
with col1:
    mic_clicked = st.button("Mic", help="Click and speak", use_container_width=True)
with col2:
    user_input = st.chat_input("Type your answer here and press Enter...")

if mic_clicked:
    with st.spinner("Listening... Please speak now"):
        spoken = record_voice()
    if spoken:
        st.toast(f"Heard: {spoken}")
        user_input = spoken
    else:
        st.warning("Could not hear clearly. Please try again or type your answer.")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "data": {}})
    response = agent.process(user_input)
    st.session_state.messages.append({
        "role":    "agent",
        "content": response["message"],
        "data":    response,
    })
    st.rerun()
