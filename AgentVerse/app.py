# app.py - ElderCare AI Agent — Elder Friendly Chat

import streamlit as st
from agent import AppointmentAgent

st.set_page_config(
    page_title="ElderCare AI Agent",
    page_icon="🏥",
    layout="centered",
)

st.markdown("""
<style>
    /* Large readable font for elders */
    html, body, [class*="css"] { font-size: 20px; font-family: Arial, sans-serif; }

    /* Header */
    .header {
        background: linear-gradient(135deg, #0d6e6e, #14a89a);
        color: white; padding: 1.5rem 2rem;
        border-radius: 14px; text-align: center; margin-bottom: 1.2rem;
    }
    .header h1 { font-size: 2.2rem; margin: 0; }
    .header p  { font-size: 1.1rem; margin: 0.4rem 0 0; opacity: 0.92; }

    /* Chat messages — bigger text */
    .stChatMessage p { font-size: 1.15rem !important; line-height: 1.8 !important; }

    /* Emergency */
    .emergency {
        background: #ffebee; border: 2px solid #e53935;
        border-radius: 10px; padding: 1rem 1.2rem; font-size: 1.2rem;
    }

    /* Big send button */
    div.stButton > button {
        font-size: 1.1rem; padding: 0.6rem 1.5rem;
        border-radius: 10px; background-color: #0d6e6e;
        color: white; border: none;
    }
    div.stButton > button:hover { background-color: #0a5555; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #e0f2f1; }

    /* Chat input bigger */
    .stChatInput textarea { font-size: 1.1rem !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — only API key + restart
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/caduceus.png", width=70)
    st.markdown("## ⚙️ Settings")
    api_key = st.text_input(
        "🔑 Gemini API Key (Optional)",
        type="password",
        placeholder="Paste your API key here",
        help="Free key: https://aistudio.google.com/app/apikey",
    )
    st.caption("Used only for AI analysis. Never stored.")
    st.divider()

    if st.button("🔄 Start Over", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("### 🤖 Agent Info")
    if "agent" in st.session_state:
        a = st.session_state.agent
        st.caption(f"Step: `{a.state}`")
        if a.patient.get("name"):
            st.caption(f"👤 {a.patient['name']}")
        if a.specialty:
            st.caption(f"🏥 {a.specialty}")

    st.divider()
    st.markdown("### ℹ️ How to use")
    st.caption(
        "1. Type your answer in the box below\n"
        "2. Press Enter to send\n"
        "3. தமிழில் பேசலாம் — Tamil also works!\n"
        "4. 🎙️ Click mic to speak"
    )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header">
    <h1>🏥 ElderCare AI</h1>
    <p>Your Personal Health Assistant — Just answer my questions!</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Init agent
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "agent":
        with st.chat_message("assistant", avatar="🏥"):
            data = msg.get("data", {})
            if data.get("emergency"):
                st.markdown(
                    f'<div class="emergency">{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(msg["content"])

            # Download button if confirmation ready
            dl = data.get("data", {}).get("download")
            if dl:
                st.download_button(
                    "📥 Download Your Appointment Confirmation",
                    data=dl,
                    file_name=data["data"]["filename"],
                    mime="text/plain",
                    key=f"dl_{id(msg)}",
                    use_container_width=True,
                )
    else:
        with st.chat_message("user", avatar="👴"):
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Voice input
# ---------------------------------------------------------------------------
def record_voice() -> str:
    try:
        import speech_recognition as sr
        r   = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=6, phrase_time_limit=10)
        # Try Tamil first, fallback to English
        try:
            return r.recognize_google(audio, language="ta-IN")
        except Exception:
            return r.recognize_google(audio, language="en-IN")
    except Exception:
        return ""

# ---------------------------------------------------------------------------
# Input row — mic + text
# ---------------------------------------------------------------------------
agent = st.session_state.agent

col1, col2 = st.columns([1, 6])
with col1:
    mic_clicked = st.button("🎙️", help="Click and speak", use_container_width=True)
with col2:
    user_input = st.chat_input("Type your answer here and press Enter...")

# Handle mic
if mic_clicked:
    with st.spinner("🎙️ Listening... Please speak now"):
        spoken = record_voice()
    if spoken:
        st.toast(f"✅ Heard: {spoken}")
        user_input = spoken
    else:
        st.warning("Could not hear clearly. Please try again or type your answer.")

# Process input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "data": {}})
    response = agent.process(user_input)
    st.session_state.messages.append({
        "role":    "agent",
        "content": response["message"],
        "data":    response,
    })
    st.rerun()
