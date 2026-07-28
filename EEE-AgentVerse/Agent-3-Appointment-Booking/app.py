# app.py - ElderCare AI Agent - Appointment Booking

import streamlit as st
from agent import AppointmentAgent

st.set_page_config(page_title="Appointment Booking Agent", layout="centered")

st.markdown("""
<style>
    body { font-family: Arial, sans-serif; }
    .chat-header {
        background: #0d6e6e;
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .chat-header h2 { margin: 0; font-size: 1.4rem; }
    .chat-header p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }
    .stChatMessage p { font-size: 1.05rem !important; line-height: 1.8 !important; }
    .emergency-box {
        background: #fff0f0;
        border: 2px solid #cc0000;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 1.05rem;
    }
    section[data-testid="stSidebar"] { background: #e8f5f5; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    api_key = st.text_input(
        "Gemini API Key (Optional)",
        type="password",
        placeholder="Paste your API key here",
        help="Free key: https://aistudio.google.com/app/apikey",
    )
    st.caption("Used only for AI symptom analysis. Never stored.")
    st.divider()

    if st.button("Start Over", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("### Agent Info")
    if "agent" in st.session_state:
        a = st.session_state.agent
        st.caption(f"Step: {a.state}")
        if a.patient.get("name"):
            st.caption(f"Patient: {a.patient['name']}")
        if a.specialty:
            st.caption(f"Specialty: {a.specialty}")

    st.divider()
    st.markdown("### How to use")
    st.caption(
        "1. Type your answer in the box below\n"
        "2. Press Enter to send\n"
        "3. Tamil also works\n"
        "4. Click mic to speak"
    )

# Header
st.markdown("""
<div class="chat-header">
    <h2>Appointment Booking Agent</h2>
    <p>ElderCare AI - I will help you book a doctor appointment step by step.</p>
</div>
""", unsafe_allow_html=True)

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
    import google.generativeai as genai
    st.session_state.agent.api_key = api_key
    genai.configure(api_key=api_key)
    st.session_state.agent.model = genai.GenerativeModel("gemini-1.5-flash")

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
