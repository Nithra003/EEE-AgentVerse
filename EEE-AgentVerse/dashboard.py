"""ElderCare AI — Unified Agent Dashboard Launcher"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from shared.ui_components import init_theme, sidebar_nav, theme_toggle
from shared.ui_theme import inject, AGENT_ACCENTS

st.set_page_config(
    page_title="ElderCare AI — Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

dark = init_theme()
inject(dark)

AGENTS = [
    {"icon": "💊", "name": "Medicine Reminder",      "desc": "Smart reminders for daily medications",        "port": 8501},
    {"icon": "🚨", "name": "Emergency Detection",    "desc": "Real-time fall and emergency monitoring",      "port": 8502},
    {"icon": "📅", "name": "Appointment Booking",    "desc": "Book doctor appointments with AI assist",      "port": 8503},
    {"icon": "📋", "name": "Prescription Explainer", "desc": "Explains prescriptions in simple language",    "port": 8504},
    {"icon": "📊", "name": "Health Report",          "desc": "Wearable data analysis and risk reports",      "port": 8505},
    {"icon": "👨👩👧", "name": "Family Notifier",       "desc": "Instant emergency alerts to family",           "port": 8506},
    {"icon": "🥗", "name": "Diet Recommendation",    "desc": "Personalized diet plans by condition",         "port": 8507},
    {"icon": "🏃", "name": "Exercise Coach",         "desc": "Safe exercise plans for elderly patients",     "port": 8508},
    {"icon": "😊", "name": "Mood Companion",         "desc": "Emotional wellness and daily support",         "port": 8509},
    {"icon": "🎙️", "name": "Voice Assistant",        "desc": "Conversational AI companion for elders",       "port": 8510},
    {"icon": "🧬", "name": "Medical Assistant",      "desc": "Full medical AI with OCR and reminders",       "port": 8511},
]

sidebar_nav()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero" role="banner">
  <div class="hero-badge">Fetch.ai AgentVerse Hackathon</div>
  <div class="hero-title">ElderCare <span class="accent">AI</span></div>
  <div class="hero-sub">11 autonomous agents working together for elder health and safety</div>
  <div class="hero-stats" role="list">
    <div class="stat" role="listitem">
      <div class="stat-num">11</div><div class="stat-lbl">Agents</div>
    </div>
    <div class="stat" role="listitem">
      <div class="stat-num"><span class="pulse-dot" aria-hidden="true"></span>Live</div>
      <div class="stat-lbl">Status</div>
    </div>
    <div class="stat" role="listitem">
      <div class="stat-num">AI</div><div class="stat-lbl">Powered</div>
    </div>
    <div class="stat" role="listitem">
      <div class="stat-num">24/7</div><div class="stat-lbl">Available</div>
    </div>
  </div>
</div>
<div class="divider"></div>
<div class="section-lbl" aria-label="Agent selection">Select an Agent to Launch</div>
""", unsafe_allow_html=True)

# ── Agent grid ────────────────────────────────────────────────────────────────
rows = [AGENTS[i:i+5] for i in range(0, len(AGENTS), 5)]
for row in rows:
    cols = st.columns(len(row))
    for col, ag, i in zip(cols, row, range(AGENTS.index(row[0]), AGENTS.index(row[0])+len(row))):
        accent = AGENT_ACCENTS[AGENTS.index(ag)]
        idx    = AGENTS.index(ag)
        with col:
            st.markdown(
                f"""
                <a href="http://localhost:{ag['port']}" target="_blank"
                   style="display:block;text-decoration:none;
                          background:#0d1526;border:1px solid #1a2840;
                          border-top:3px solid {accent};border-radius:16px;
                          padding:1.2rem 0.8rem 1rem;text-align:center;">
                  <div style="font-size:1.6rem;margin-bottom:0.6rem;">{ag['icon']}</div>
                  <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
                              text-transform:uppercase;color:{accent};margin-bottom:0.2rem;">Agent {idx+1:02d}</div>
                  <div style="font-size:0.85rem;font-weight:600;color:#e2eaf5;
                              margin-bottom:0.25rem;">{ag['name']}</div>
                  <div style="font-size:0.68rem;color:#445566;line-height:1.4;">{ag['desc']}</div>
                  <div style="margin-top:0.6rem;font-size:0.62rem;font-weight:600;
                              color:{accent};border:1px solid #1a2840;border-radius:999px;
                              padding:0.15rem 0.5rem;display:inline-block;">:{ag['port']}</div>
                </a>
                """,
                unsafe_allow_html=True,
            )

# ── How-to section ────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with st.expander("📱 How to access from mobile", expanded=False):
    steps = [
        ("1", "Run <code>run_all_agents.bat</code> on your PC to start all 10 agents"),
        ("2", "Open Command Prompt and run <code>ipconfig</code> to find your PC's IP address"),
        ("3", "Connect your mobile to the <strong>same WiFi network</strong> as your PC"),
        ("4", "Open your mobile browser and go to <code>http://YOUR-PC-IP:8500</code>"),
        ("5", "Tap any agent card above to open it directly on your mobile browser"),
    ]
    for num, text in steps:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:0.9rem;margin-bottom:0.75rem;">
          <div style="min-width:26px;height:26px;border-radius:50%;
                      background:var(--surface2);border:1px solid var(--border2);
                      color:var(--accent);font-size:0.72rem;font-weight:700;
                      display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            {num}
          </div>
          <div style="font-size:0.83rem;color:var(--text2);line-height:1.55;padding-top:3px;">
            {text}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;font-size:0.7rem;color:var(--text3);
            margin:1.5rem 0 0.5rem;letter-spacing:0.05em;">
  ElderCare AI &nbsp;·&nbsp; Fetch.ai AgentVerse Hackathon &nbsp;·&nbsp;
  Built with ❤️ using Python, Streamlit, uAgents, Gemini AI &amp; Anthropic Claude
</div>
""", unsafe_allow_html=True)
