"""
main_app.py  —  ElderCare AI Agent
Single Streamlit app: Dashboard + 10 agents, all in one.
Run: streamlit run main_app.py
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="ElderCare AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #f8fafc !important;
    font-family: 'Inter', sans-serif;
    color: #1e293b;
}
[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stSidebar"] { display: none !important; }

/* ── top nav ── */
.nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.9rem 2rem;
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    position: sticky; top: 0; z-index: 100;
    animation: slideDown 0.4s ease both;
}
.nav-brand { font-size: 1.1rem; font-weight: 700; color: #1e293b; letter-spacing: -0.02em; }
.nav-brand span { color: #2563eb; }
.nav-back {
    font-size: 0.82rem; font-weight: 500; color: #64748b;
    cursor: pointer; padding: 0.35rem 0.9rem;
    border: 1px solid #e2e8f0; border-radius: 6px;
    background: #f8fafc; transition: all 0.2s;
    text-decoration: none;
}
.nav-back:hover { border-color: #2563eb; color: #2563eb; background: #eff6ff; }

/* ── hero ── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    animation: fadeUp 0.6s ease both;
}
.hero-badge {
    display: inline-block;
    background: #eff6ff; color: #2563eb;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.3rem 1rem; border-radius: 999px;
    border: 1px solid #bfdbfe;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 700; color: #0f172a;
    letter-spacing: -0.03em; line-height: 1.1;
}
.hero-title span { color: #2563eb; }
.hero-sub {
    margin-top: 0.8rem;
    font-size: 1rem; color: #64748b; font-weight: 400;
}
.hero-stats {
    display: flex; justify-content: center; gap: 2.5rem;
    margin-top: 2rem;
}
.stat { text-align: center; }
.stat-num { font-size: 1.8rem; font-weight: 700; color: #2563eb; }
.stat-lbl { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }

/* ── section label ── */
.section-lbl {
    text-align: center;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: #94a3b8; margin: 2rem 0 1.2rem;
}

/* ── agent grid ── */
.agent-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 0 1rem 3rem;
    max-width: 1100px;
    margin: 0 auto;
}
.agent-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem 1.2rem 1.2rem;
    cursor: pointer;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: cardPop 0.5s ease both;
    text-align: center;
}
.agent-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(37,99,235,0.1);
    border-color: #93c5fd;
}
.agent-icon-wrap {
    width: 52px; height: 52px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.9rem;
    font-size: 1.4rem;
    font-weight: 700;
}
.agent-num { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.3rem; }
.agent-name { font-size: 0.92rem; font-weight: 600; color: #1e293b; margin-bottom: 0.3rem; }
.agent-desc { font-size: 0.75rem; color: #94a3b8; line-height: 1.4; }

/* ── chat page ── */
.chat-header {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 1.2rem 2rem;
    animation: slideDown 0.4s ease both;
}
.chat-header h2 { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }
.chat-header p  { font-size: 0.82rem; color: #64748b; margin: 0.2rem 0 0; }

.tool-tag {
    display: inline-block;
    background: #eff6ff; color: #2563eb;
    font-size: 0.68rem; font-weight: 600;
    padding: 0.15rem 0.6rem; border-radius: 4px;
    margin-bottom: 0.4rem; letter-spacing: 0.06em; text-transform: uppercase;
    border: 1px solid #bfdbfe;
}
.question-tag {
    display: inline-block;
    background: #f5f3ff; color: #7c3aed;
    font-size: 0.68rem; font-weight: 600;
    padding: 0.15rem 0.6rem; border-radius: 4px;
    margin-bottom: 0.4rem; letter-spacing: 0.06em; text-transform: uppercase;
    border: 1px solid #ddd6fe;
}
.emergency-tag {
    display: inline-block;
    background: #fef2f2; color: #dc2626;
    font-size: 0.68rem; font-weight: 700;
    padding: 0.15rem 0.6rem; border-radius: 4px;
    margin-bottom: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase;
    border: 1px solid #fecaca;
}
.emergency-box {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 10px; padding: 1rem 1.2rem; color: #991b1b;
}

.progress-wrap {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 0.7rem 1rem;
    margin: 0.5rem 1rem 0.8rem; font-size: 0.78rem; color: #64748b;
}
.progress-bar-outer {
    background: #e2e8f0; border-radius: 999px;
    height: 4px; margin-top: 0.4rem; overflow: hidden;
}
.progress-bar-inner {
    height: 4px; border-radius: 999px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    transition: width 0.4s ease;
}

.stChatMessage { animation: fadeUp 0.3s ease both; }
.stChatMessage p { font-size: 0.97rem !important; line-height: 1.85 !important; color: #1e293b !important; }

[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #1e293b !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.08) !important;
}

.stButton > button {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.45rem 0.6rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    border-color: #2563eb !important;
    color: #2563eb !important;
    background: #eff6ff !important;
}

.response-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.9rem;
    line-height: 1.8;
    color: #334155;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeDown { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }
@keyframes slideDown { from { opacity:0; transform:translateY(-8px); } to { opacity:1; transform:translateY(0); } }
@keyframes cardPop {
    from { opacity: 0; transform: scale(0.94) translateY(10px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── agent definitions ─────────────────────────────────────────────────────────
AGENTS = [
    {"id": "medicine",      "name": "Medicine Reminder",     "desc": "Smart reminders for daily medications",         "color": "#eff6ff", "accent": "#2563eb", "icon": "Rx"},
    {"id": "emergency",     "name": "Emergency Detection",   "desc": "Real-time fall and emergency monitoring",       "color": "#fef2f2", "accent": "#dc2626", "icon": "SOS"},
    {"id": "appointment",   "name": "Appointment Booking",   "desc": "Book doctor appointments with AI assist",       "color": "#f0fdf4", "accent": "#16a34a", "icon": "Dr"},
    {"id": "prescription",  "name": "Prescription Explainer","desc": "Explains prescriptions in simple language",     "color": "#faf5ff", "accent": "#7c3aed", "icon": "Rx"},
    {"id": "health",        "name": "Health Report",         "desc": "Wearable data analysis and risk reports",       "color": "#fff7ed", "accent": "#ea580c", "icon": "HR"},
    {"id": "family",        "name": "Family Notifier",       "desc": "Instant emergency alerts to family",            "color": "#fdf4ff", "accent": "#a21caf", "icon": "SOS"},
    {"id": "diet",          "name": "Diet Recommendation",   "desc": "Personalized diet plans by condition",          "color": "#f0fdf4", "accent": "#15803d", "icon": "Dt"},
    {"id": "exercise",      "name": "Exercise Coach",        "desc": "Safe exercise plans for elderly patients",      "color": "#eff6ff", "accent": "#0284c7", "icon": "Ex"},
    {"id": "mood",          "name": "Mood Companion",        "desc": "Emotional wellness and daily support",          "color": "#fdf4ff", "accent": "#9333ea", "icon": "Md"},
    {"id": "voice",         "name": "Voice Assistant",       "desc": "Conversational AI companion for elders",        "color": "#f0fdfa", "accent": "#0d9488", "icon": "AI"},
]

AGENT_TOOL_MAP = {
    "medicine":     "medicine_reminder",
    "emergency":    "emergency_detection",
    "appointment":  "appointment_booking",
    "prescription": "prescription_explainer",
    "health":       "health_report",
    "family":       "family_notifier",
    "diet":         "diet_recommendation",
    "exercise":     "exercise_coach",
    "mood":         "mood_companion",
    "voice":        "general_assistant",
}

# ── session init ──────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page     = "dashboard"
if "agent_id" not in st.session_state:
    st.session_state.agent_id = None
if "agents" not in st.session_state:
    st.session_state.agents   = {}   # one ElderCareAgent per agent_id
if "messages" not in st.session_state:
    st.session_state.messages = {}   # messages per agent_id

# ── nav bar ───────────────────────────────────────────────────────────────────
col_nav1, col_nav2 = st.columns([6, 1])
with col_nav1:
    st.markdown('<div class="nav-brand">ElderCare <span>AI</span></div>', unsafe_allow_html=True)
with col_nav2:
    if st.session_state.page != "dashboard":
        if st.button("Back to Dashboard"):
            st.session_state.page     = "dashboard"
            st.session_state.agent_id = None
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    st.markdown("""
    <div class="hero">
        <div class="hero-badge">AgentVerse Hackathon &nbsp;·&nbsp; EEE Team</div>
        <div class="hero-title">ElderCare <span>AI</span></div>
        <div class="hero-sub">10 intelligent agents working together for elder health and safety</div>
        <div class="hero-stats">
            <div class="stat"><div class="stat-num">10</div><div class="stat-lbl">Agents</div></div>
            <div class="stat"><div class="stat-num">AI</div><div class="stat-lbl">Powered</div></div>
            <div class="stat"><div class="stat-num">24/7</div><div class="stat-lbl">Available</div></div>
        </div>
    </div>
    <div class="section-lbl">Select an Agent to Start</div>
    """, unsafe_allow_html=True)

    # render agent cards as Streamlit buttons in a grid
    cols = st.columns(5)
    for i, ag in enumerate(AGENTS):
        with cols[i % 5]:
            st.markdown(f"""
            <div class="agent-card" style="border-top: 3px solid {ag['accent']};">
                <div class="agent-icon-wrap" style="background:{ag['color']}; color:{ag['accent']};">
                    {ag['icon']}
                </div>
                <div class="agent-num" style="color:{ag['accent']};">Agent {i+1:02d}</div>
                <div class="agent-name">{ag['name']}</div>
                <div class="agent-desc">{ag['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open", key=f"open_{ag['id']}", use_container_width=True):
                st.session_state.page     = "chat"
                st.session_state.agent_id = ag["id"]
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    from eldercare_agent import ElderCareAgent

    aid  = st.session_state.agent_id
    ag   = next(a for a in AGENTS if a["id"] == aid)
    tool = AGENT_TOOL_MAP[aid]

    # init agent and messages for this agent
    if aid not in st.session_state.agents:
        ec_agent = ElderCareAgent()
        # pre-set the tool so it goes directly to the right flow
        ec_agent.current_tool = tool
        st.session_state.agents[aid]   = ec_agent
        st.session_state.messages[aid] = []

        # welcome message
        welcome_map = {
            "medicine":     "Hello! I am your Medicine Reminder Agent.\n\nI will help you set up medicine reminders and track your medication schedule.\n\nShall we get started?",
            "emergency":    "Hello! I am your Emergency Detection Agent.\n\nI am here to help in case of any emergency — falls, chest pain, or any urgent situation.\n\nHow can I help you right now?",
            "appointment":  "Hello! I am your Appointment Booking Agent.\n\nI will help you find the right doctor and book an appointment based on your symptoms.\n\nShall we get started?",
            "prescription": "Hello! I am your Prescription Explainer Agent.\n\nI will explain your medicine prescription in simple, easy-to-understand language.\n\nShall we get started?",
            "health":       "Hello! I am your Health Report Agent.\n\nI will analyze your health readings and give you a complete health report.\n\nShall we get started?",
            "family":       "Hello! I am your Family Notifier Agent.\n\nI will help you send emergency alerts to your family members immediately.\n\nShall we get started?",
            "diet":         "Hello! I am your Diet Recommendation Agent.\n\nI will create a personalized diet plan based on your health condition.\n\nShall we get started?",
            "exercise":     "Hello! I am your Exercise Coach Agent.\n\nI will create a safe and gentle exercise plan suited for your health condition.\n\nShall we get started?",
            "mood":         "Hello! I am your Mood Companion Agent.\n\nI am here to support your emotional wellness and daily positivity.\n\nHow are you feeling today?",
            "voice":        "Hello! I am your AI Voice Assistant.\n\nI am here to have a conversation with you, answer your questions, and keep you company.\n\nWhat would you like to talk about?",
        }
        st.session_state.messages[aid].append({
            "role": "assistant", "content": welcome_map[aid],
            "tool": "", "is_question": False, "emergency": False,
        })

    ec_agent = st.session_state.agents[aid]
    msgs     = st.session_state.messages[aid]

    # ── chat header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="chat-header" style="border-left: 4px solid {ag['accent']};">
        <h2>{ag['name']}</h2>
        <p>ElderCare AI &nbsp;·&nbsp; {ag['desc']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── progress bar ──────────────────────────────────────────────────────────
    if getattr(ec_agent, "collecting", False) and getattr(ec_agent, "flow", []):
        total = len(ec_agent.flow)
        done  = ec_agent.flow_index
        pct   = int((done / total) * 100)
        st.markdown(
            f'<div class="progress-wrap">'
            f'Collecting information &nbsp;—&nbsp; Question {done + 1} of {total}'
            f'<div class="progress-bar-outer">'
            f'<div class="progress-bar-inner" style="width:{pct}%"></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    # ── quick suggestions (only when not collecting) ──────────────────────────
    clicked = None
    if not getattr(ec_agent, "collecting", False):
        suggestion_map = {
            "medicine":     ["Set a medicine reminder", "I forgot my medicine", "What is my dosage?"],
            "emergency":    ["I fell down", "I have chest pain", "I need help"],
            "appointment":  ["I have knee pain", "I have fever and cough", "I need a heart checkup"],
            "prescription": ["Explain paracetamol", "Explain metformin", "What are the side effects?"],
            "health":       ["Check my health report", "My BP is 140/90", "My sugar is 180"],
            "family":       ["Alert my family", "Send emergency notification", "Notify my son"],
            "diet":         ["Diet plan for diabetes", "What should I eat?", "Foods to avoid"],
            "exercise":     ["Exercise for arthritis", "Beginner workout plan", "Safe exercises for me"],
            "mood":         ["I feel sad today", "I am feeling lonely", "I am anxious"],
            "voice":        ["How are you?", "Tell me something positive", "I want to talk"],
        }
        suggs = suggestion_map.get(aid, [])
        if suggs:
            scols = st.columns(len(suggs))
            for si, s in enumerate(suggs):
                if scols[si].button(s, key=f"sugg_{aid}_{si}", use_container_width=True):
                    clicked = s

    # ── render messages ───────────────────────────────────────────────────────
    for msg in msgs:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                if msg.get("emergency"):
                    st.markdown('<div class="emergency-tag">Emergency Alert</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="emergency-box">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    if msg.get("is_question"):
                        st.markdown('<div class="question-tag">Agent Question</div>', unsafe_allow_html=True)
                        st.markdown(msg["content"])
                    elif msg.get("tool"):
                        st.markdown(f'<div class="tool-tag">{msg["tool"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="response-box">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(msg["content"])
        else:
            with st.chat_message("user"):
                st.markdown(msg["content"])

    # ── input ─────────────────────────────────────────────────────────────────
    placeholder = "Answer the question above..." if getattr(ec_agent, "collecting", False) else f"Talk to {ag['name']}..."
    user_input  = st.chat_input(placeholder)

    if clicked:
        user_input = clicked

    if user_input:
        msgs.append({
            "role": "user", "content": user_input,
            "tool": "", "is_question": False, "emergency": False,
        })

        # force the agent to use the correct tool for this page
        if not getattr(ec_agent, "collecting", False):
            ec_agent.current_tool = tool

        with st.spinner("Thinking..."):
            result = ec_agent.process(user_input)

        is_emergency = (
            result.get("tool_used") == "Emergency Detection"
            and "EMERGENCY" in result["message"].upper()
        )

        msgs.append({
            "role":        "assistant",
            "content":     result["message"],
            "tool":        result.get("tool_used", ""),
            "is_question": result.get("is_question", False),
            "emergency":   is_emergency,
        })
        st.rerun()
