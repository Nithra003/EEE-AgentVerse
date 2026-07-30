"""
main_app.py — ElderCare AI · Unified Dashboard
Run: streamlit run main_app.py
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from shared.ui_components import (
    init_theme, sidebar_nav, language_selector, voice_input,
    tts_button, progress_bar, agent_header, event_banner,
)
from shared.ui_theme import inject, AGENT_ACCENTS

st.set_page_config(
    page_title="ElderCare AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
dark = init_theme()
inject(dark)

# ── Agent definitions ─────────────────────────────────────────────────────────
AGENTS = [
    {"id": "medicine",     "name": "Medicine Reminder",      "desc": "Smart reminders for daily medications",        "icon": "💊", "port": 8501},
    {"id": "emergency",    "name": "Emergency Detection",    "desc": "Real-time fall and emergency monitoring",      "icon": "🚨", "port": 8502},
    {"id": "appointment",  "name": "Appointment Booking",    "desc": "Book doctor appointments with AI assist",      "icon": "📅", "port": 8503},
    {"id": "prescription", "name": "Prescription Explainer", "desc": "Explains prescriptions in simple language",    "icon": "📋", "port": 8504},
    {"id": "health",       "name": "Health Report",          "desc": "Wearable data analysis and risk reports",      "icon": "📊", "port": 8505},
    {"id": "family",       "name": "Family Notifier",        "desc": "Instant emergency alerts to family",           "icon": "👨‍👩‍👧", "port": 8506},
    {"id": "diet",         "name": "Diet Recommendation",    "desc": "Personalized diet plans by condition",         "icon": "🥗", "port": 8507},
    {"id": "exercise",     "name": "Exercise Coach",         "desc": "Safe exercise plans for elderly patients",     "icon": "🏃", "port": 8508},
    {"id": "mood",         "name": "Mood Companion",         "desc": "Emotional wellness and daily support",         "icon": "😊", "port": 8509},
    {"id": "voice",        "name": "Voice Assistant",        "desc": "Conversational AI companion for elders",       "icon": "🎙️", "port": 8510},
]

WELCOME_MAP = {
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

SUGGESTIONS = {
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

AGENT_TOOL_MAP = {
    "medicine": "medicine_reminder", "emergency": "emergency_detection",
    "appointment": "appointment_booking", "prescription": "prescription_explainer",
    "health": "health_report", "family": "family_notifier",
    "diet": "diet_recommendation", "exercise": "exercise_coach",
    "mood": "mood_companion", "voice": "general_assistant",
}

# ── Session init ──────────────────────────────────────────────────────────────
for k, v in {
    "page": "dashboard", "agent_id": None,
    "agents": {}, "messages": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav(active_id=st.session_state.get("agent_id") or "")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    # Hero
    st.markdown("""
    <div class="hero" role="banner">
      <div class="hero-badge">AgentVerse Hackathon &nbsp;·&nbsp; EEE Team</div>
      <div class="hero-title">ElderCare <span class="accent">AI</span></div>
      <div class="hero-sub">10 intelligent agents working together for elder health and safety</div>
      <div class="hero-stats" role="list">
        <div class="stat" role="listitem"><div class="stat-num">10</div><div class="stat-lbl">Agents</div></div>
        <div class="stat" role="listitem"><div class="stat-num"><span class="pulse-dot" aria-hidden="true"></span>Live</div><div class="stat-lbl">Status</div></div>
        <div class="stat" role="listitem"><div class="stat-num">24/7</div><div class="stat-lbl">Available</div></div>
        <div class="stat" role="listitem"><div class="stat-num">AI</div><div class="stat-lbl">Powered</div></div>
      </div>
    </div>
    <div class="section-lbl" aria-label="Agent selection">Select an Agent to Start</div>
    """, unsafe_allow_html=True)

    # Agent grid — 5 columns on desktop, 2 on mobile
    cols = st.columns(5, gap="small")
    for i, ag in enumerate(AGENTS):
        accent = AGENT_ACCENTS[i]
        with cols[i % 5]:
            st.markdown(f"""
            <div class="agent-card"
                 style="--card-accent:{accent};--card-shadow:rgba(0,0,0,0.25);
                        border-top:3px solid {accent};"
                 role="article" aria-label="{ag['name']} agent">
              <div class="agent-icon-wrap" aria-hidden="true"
                   style="border-color:{accent};box-shadow:0 0 16px {accent}22;">
                {ag['icon']}
              </div>
              <div class="agent-num">Agent {i+1:02d}</div>
              <div class="agent-name">{ag['name']}</div>
              <div class="agent-desc">{ag['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(
                f"Open {ag['name']}",
                key=f"open_{ag['id']}",
                use_container_width=True,
                help=ag["desc"],
            ):
                st.session_state.page = "chat"
                st.session_state.agent_id = ag["id"]
                st.rerun()

    # How-to section
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    with st.expander("📱 How to access from mobile", expanded=False):
        steps = [
            ("Run", "Run <code>run_all_agents.bat</code> on your PC to start all agents"),
            ("Find IP", "Run <code>ipconfig</code> in Command Prompt to find your PC IP"),
            ("Connect", "Connect your mobile to the same WiFi network as your PC"),
            ("Open", "Open mobile browser → <code>http://YOUR-PC-IP:8500</code>"),
            ("Use", "Tap any agent card to open it directly on your mobile"),
        ]
        for step, text in steps:
            st.markdown(
                f'<div style="display:flex;gap:0.8rem;align-items:flex-start;margin-bottom:0.6rem;">'
                f'<span style="min-width:60px;font-size:0.68rem;font-weight:700;color:var(--accent);'
                f'text-transform:uppercase;letter-spacing:0.08em;padding-top:2px;">{step}</span>'
                f'<span style="font-size:0.82rem;color:var(--text2);line-height:1.5;">{text}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div style="text-align:center;font-size:0.7rem;color:var(--text3);margin-top:2rem;">'
        'ElderCare AI — Fetch.ai AgentVerse Hackathon · Built with ❤️ by EEE Team</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AGENT CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":
    from eldercare_agent import ElderCareAgent

    aid  = st.session_state.agent_id
    ag   = next(a for a in AGENTS if a["id"] == aid)
    tool = AGENT_TOOL_MAP[aid]
    accent = AGENT_ACCENTS[next(i for i, a in enumerate(AGENTS) if a["id"] == aid)]

    # Init agent + messages
    if aid not in st.session_state.agents:
        ec = ElderCareAgent()
        ec.current_tool = tool
        st.session_state.agents[aid] = ec
        st.session_state.messages[aid] = [{
            "role": "assistant", "content": WELCOME_MAP[aid],
            "tool": "", "is_question": False, "emergency": False,
        }]

    ec_agent = st.session_state.agents[aid]
    msgs     = st.session_state.messages[aid]

    # Header
    agent_header(
        title=f"{ag['icon']} {ag['name']}",
        subtitle=f"ElderCare AI · {ag['desc']}",
        accent=accent,
    )

    # Back button
    if st.button("← Back to Dashboard", key="back_btn"):
        st.session_state.page = "dashboard"
        st.session_state.agent_id = None
        st.rerun()

    # Language + voice row
    lang_col, voice_col, tts_col = st.columns([2, 1, 1])
    with lang_col:
        lang = language_selector(key=f"lang_{aid}")
    with voice_col:
        spoken = voice_input(lang_code=lang["code"], key=f"voice_{aid}")
    with tts_col:
        last_reply = next(
            (m["content"] for m in reversed(msgs) if m["role"] == "assistant"), ""
        )
        tts_button(last_reply, lang_code=lang["code"], key=f"tts_{aid}")

    # Progress bar
    if getattr(ec_agent, "collecting", False) and getattr(ec_agent, "flow", []):
        total = len(ec_agent.flow)
        done  = ec_agent.flow_index
        progress_bar(done + 1, total, "Collecting information")

    # Quick suggestions
    clicked = None
    if not getattr(ec_agent, "collecting", False):
        suggs = SUGGESTIONS.get(aid, [])
        if suggs:
            st.markdown(
                '<div style="font-size:0.7rem;color:var(--text3);margin-bottom:0.4rem;">'
                'Quick suggestions:</div>',
                unsafe_allow_html=True,
            )
            scols = st.columns(len(suggs))
            for si, s in enumerate(suggs):
                if scols[si].button(s, key=f"sugg_{aid}_{si}", use_container_width=True):
                    clicked = s

    # Messages
    for msg in msgs:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar=ag["icon"]):
                if msg.get("emergency"):
                    st.markdown(
                        '<span class="tag tag-emergency" role="alert">🚨 Emergency Alert</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="emergency-box" role="alert">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                elif msg.get("is_question"):
                    st.markdown(
                        '<span class="tag tag-question">❓ Agent Question</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(msg["content"])
                elif msg.get("tool"):
                    st.markdown(
                        f'<span class="tag tag-tool">{msg["tool"]}</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="response-box">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(msg["content"])
        else:
            with st.chat_message("user"):
                st.markdown(msg["content"])

    # Input
    placeholder = (
        "Answer the question above..."
        if getattr(ec_agent, "collecting", False)
        else f"Talk to {ag['name']}..."
    )
    user_input = st.chat_input(placeholder)

    # Voice input takes priority if spoken
    if spoken and spoken != st.session_state.get(f"_last_spoken_{aid}", ""):
        st.session_state[f"_last_spoken_{aid}"] = spoken
        user_input = spoken

    if clicked:
        user_input = clicked

    if user_input:
        msgs.append({
            "role": "user", "content": user_input,
            "tool": "", "is_question": False, "emergency": False,
        })
        if not getattr(ec_agent, "collecting", False):
            ec_agent.current_tool = tool

        with st.spinner("Thinking…"):
            result = ec_agent.process(user_input)

        is_emergency = (
            result.get("tool_used") == "Emergency Detection"
            and "EMERGENCY" in result["message"].upper()
        )
        msgs.append({
            "role": "assistant", "content": result["message"],
            "tool": result.get("tool_used", ""),
            "is_question": result.get("is_question", False),
            "emergency": is_emergency,
        })
        st.rerun()
