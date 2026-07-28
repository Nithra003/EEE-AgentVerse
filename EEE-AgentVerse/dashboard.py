"""ElderCare AI - Unified Agent Dashboard Launcher"""

import streamlit as st

st.set_page_config(
    page_title="ElderCare AI - AgentVerse",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body, [data-testid="stAppViewContainer"] {
    background: #0a0e1a !important;
    font-family: 'Inter', sans-serif;
  }

  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stToolbar"] { display: none; }
  footer { display: none; }
  #MainMenu { display: none; }
  [data-testid="stSidebar"] { display: none; }

  .hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
    position: relative;
  }

  .hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e3a5f, #0d2137);
    border: 1px solid #2a5298;
    color: #7eb8f7;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
    animation: fadeSlideDown 0.6s ease both;
  }

  .hero-title {
    font-size: clamp(2rem, 6vw, 3.2rem);
    font-weight: 700;
    color: #ffffff;
    line-height: 1.15;
    animation: fadeSlideDown 0.7s ease both;
  }

  .hero-title span {
    background: linear-gradient(90deg, #4f9cf9, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-sub {
    color: #8899aa;
    font-size: 1rem;
    margin-top: 0.8rem;
    font-weight: 300;
    animation: fadeSlideDown 0.8s ease both;
  }

  .stats-row {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 2rem auto 0;
    animation: fadeSlideDown 0.9s ease both;
  }

  .stat-item {
    text-align: center;
  }

  .stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: #4f9cf9;
  }

  .stat-label {
    font-size: 0.72rem;
    color: #556677;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
  }

  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e2d45, transparent);
    margin: 2rem 0;
  }

  .section-label {
    text-align: center;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #445566;
    margin-bottom: 1.5rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
    padding: 0 0.5rem;
  }

  @media (max-width: 480px) {
    .grid { grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  }

  .agent-card {
    background: #0d1526;
    border: 1px solid #1a2840;
    border-radius: 16px;
    padding: 1.4rem 1rem 1.2rem;
    text-align: center;
    cursor: pointer;
    text-decoration: none;
    display: block;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    animation: cardPop 0.5s ease both;
    position: relative;
    overflow: hidden;
  }

  .agent-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--card-glow);
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: 16px;
  }

  .agent-card:hover::before { opacity: 1; }

  .agent-card:hover {
    transform: translateY(-4px) scale(1.02);
    border-color: var(--card-accent);
    box-shadow: 0 12px 32px var(--card-shadow);
  }

  .agent-card:nth-child(1)  { --card-accent:#4f9cf9; --card-shadow:rgba(79,156,249,0.2); --card-glow:linear-gradient(135deg,rgba(79,156,249,0.06),transparent); animation-delay:0.05s; }
  .agent-card:nth-child(2)  { --card-accent:#f87171; --card-shadow:rgba(248,113,113,0.2); --card-glow:linear-gradient(135deg,rgba(248,113,113,0.06),transparent); animation-delay:0.10s; }
  .agent-card:nth-child(3)  { --card-accent:#34d399; --card-shadow:rgba(52,211,153,0.2); --card-glow:linear-gradient(135deg,rgba(52,211,153,0.06),transparent); animation-delay:0.15s; }
  .agent-card:nth-child(4)  { --card-accent:#a78bfa; --card-shadow:rgba(167,139,250,0.2); --card-glow:linear-gradient(135deg,rgba(167,139,250,0.06),transparent); animation-delay:0.20s; }
  .agent-card:nth-child(5)  { --card-accent:#38bdf8; --card-shadow:rgba(56,189,248,0.2); --card-glow:linear-gradient(135deg,rgba(56,189,248,0.06),transparent); animation-delay:0.25s; }
  .agent-card:nth-child(6)  { --card-accent:#fb923c; --card-shadow:rgba(251,146,60,0.2);  --card-glow:linear-gradient(135deg,rgba(251,146,60,0.06),transparent);  animation-delay:0.30s; }
  .agent-card:nth-child(7)  { --card-accent:#4ade80; --card-shadow:rgba(74,222,128,0.2);  --card-glow:linear-gradient(135deg,rgba(74,222,128,0.06),transparent);  animation-delay:0.35s; }
  .agent-card:nth-child(8)  { --card-accent:#60a5fa; --card-shadow:rgba(96,165,250,0.2);  --card-glow:linear-gradient(135deg,rgba(96,165,250,0.06),transparent);  animation-delay:0.40s; }
  .agent-card:nth-child(9)  { --card-accent:#e879f9; --card-shadow:rgba(232,121,249,0.2); --card-glow:linear-gradient(135deg,rgba(232,121,249,0.06),transparent); animation-delay:0.45s; }
  .agent-card:nth-child(10) { --card-accent:#2dd4bf; --card-shadow:rgba(45,212,191,0.2);  --card-glow:linear-gradient(135deg,rgba(45,212,191,0.06),transparent);  animation-delay:0.50s; }

  .agent-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 0.9rem;
    font-size: 1.5rem;
    background: var(--card-glow-solid, #111d30);
    border: 1px solid var(--card-accent);
    box-shadow: 0 0 16px var(--card-shadow);
  }

  .agent-num {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--card-accent);
    text-transform: uppercase;
    margin-bottom: 0.3rem;
  }

  .agent-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: #dde8f5;
    line-height: 1.3;
    margin-bottom: 0.4rem;
  }

  .agent-desc {
    font-size: 0.72rem;
    color: #445566;
    line-height: 1.4;
  }

  .agent-port {
    display: inline-block;
    margin-top: 0.7rem;
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--card-accent);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 999px;
    padding: 0.2rem 0.6rem;
    letter-spacing: 0.05em;
  }

  .pulse-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 5px;
    animation: pulse 2s infinite;
    vertical-align: middle;
  }

  .how-to {
    background: #0d1526;
    border: 1px solid #1a2840;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 2rem 0.5rem 0;
  }

  .how-to-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4f9cf9;
    margin-bottom: 1rem;
  }

  .how-to-step {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
  }

  .step-num {
    min-width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1e3a5f, #0d2137);
    border: 1px solid #2a5298;
    color: #4f9cf9;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .step-text {
    font-size: 0.82rem;
    color: #7a8fa8;
    line-height: 1.5;
    padding-top: 0.1rem;
  }

  .step-text code {
    background: #111d30;
    border: 1px solid #1e3a5f;
    color: #4f9cf9;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.78rem;
  }

  .footer-note {
    text-align: center;
    font-size: 0.72rem;
    color: #2a3a4a;
    margin: 2rem 0 1rem;
    letter-spacing: 0.05em;
  }

  @keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes cardPop {
    from { opacity: 0; transform: scale(0.92) translateY(12px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
  }

  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }
    50%       { box-shadow: 0 0 0 5px rgba(34,197,94,0); }
  }

  @keyframes scanline {
    0%   { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
  }

  .scanline {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(79,156,249,0.15), transparent);
    animation: scanline 6s linear infinite;
    pointer-events: none;
    z-index: 9999;
  }
</style>

<div class="scanline"></div>

<div class="hero">
  <div class="hero-badge">Fetch.ai AgentVerse Hackathon</div>
  <div class="hero-title">ElderCare <span>AI</span></div>
  <div class="hero-sub">10 autonomous agents working together for elder health and safety</div>
  <div class="stats-row">
    <div class="stat-item">
      <div class="stat-num">10</div>
      <div class="stat-label">Agents</div>
    </div>
    <div class="stat-item">
      <div class="stat-num"><span class="pulse-dot"></span>Live</div>
      <div class="stat-label">Status</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">AI</div>
      <div class="stat-label">Powered</div>
    </div>
  </div>
</div>

<div class="divider"></div>
<div class="section-label">Select an Agent to Launch</div>

<div class="grid">

  <a class="agent-card" href="http://localhost:8501" target="_blank">
    <div class="agent-icon">💊</div>
    <div class="agent-num">Agent 01</div>
    <div class="agent-name">Medicine Reminder</div>
    <div class="agent-desc">Smart reminders for daily medications</div>
    <div class="agent-port">:8501</div>
  </a>

  <a class="agent-card" href="http://localhost:8502" target="_blank">
    <div class="agent-icon">🚨</div>
    <div class="agent-num">Agent 02</div>
    <div class="agent-name">Emergency Detection</div>
    <div class="agent-desc">Real-time fall and emergency monitoring</div>
    <div class="agent-port">:8502</div>
  </a>

  <a class="agent-card" href="http://localhost:8503" target="_blank">
    <div class="agent-icon">📅</div>
    <div class="agent-num">Agent 03</div>
    <div class="agent-name">Appointment Booking</div>
    <div class="agent-desc">Book doctor appointments with AI assist</div>
    <div class="agent-port">:8503</div>
  </a>

  <a class="agent-card" href="http://localhost:8504" target="_blank">
    <div class="agent-icon">📋</div>
    <div class="agent-num">Agent 04</div>
    <div class="agent-name">Prescription Explainer</div>
    <div class="agent-desc">Explains prescriptions in simple language</div>
    <div class="agent-port">:8504</div>
  </a>

  <a class="agent-card" href="http://localhost:8505" target="_blank">
    <div class="agent-icon">📊</div>
    <div class="agent-num">Agent 05</div>
    <div class="agent-name">Health Report</div>
    <div class="agent-desc">Wearable data analysis and risk reports</div>
    <div class="agent-port">:8505</div>
  </a>

  <a class="agent-card" href="http://localhost:8506" target="_blank">
    <div class="agent-icon">📣</div>
    <div class="agent-num">Agent 06</div>
    <div class="agent-name">Family Notifier</div>
    <div class="agent-desc">Instant emergency alerts to family</div>
    <div class="agent-port">:8506</div>
  </a>

  <a class="agent-card" href="http://localhost:8507" target="_blank">
    <div class="agent-icon">🥗</div>
    <div class="agent-num">Agent 07</div>
    <div class="agent-name">Diet Recommendation</div>
    <div class="agent-desc">Personalized diet plans by condition</div>
    <div class="agent-port">:8507</div>
  </a>

  <a class="agent-card" href="http://localhost:8508" target="_blank">
    <div class="agent-icon">🏃</div>
    <div class="agent-num">Agent 08</div>
    <div class="agent-name">Exercise Coach</div>
    <div class="agent-desc">Safe exercise plans for elderly patients</div>
    <div class="agent-port">:8508</div>
  </a>

  <a class="agent-card" href="http://localhost:8509" target="_blank">
    <div class="agent-icon">🧠</div>
    <div class="agent-num">Agent 09</div>
    <div class="agent-name">Mood Companion</div>
    <div class="agent-desc">Emotional wellness and daily support</div>
    <div class="agent-port">:8509</div>
  </a>

  <a class="agent-card" href="http://localhost:8510" target="_blank">
    <div class="agent-icon">🎙</div>
    <div class="agent-num">Agent 10</div>
    <div class="agent-name">Voice Assistant</div>
    <div class="agent-desc">Conversational AI companion for elders</div>
    <div class="agent-port">:8510</div>
  </a>

</div>

<div class="how-to">
  <div class="how-to-title">How to access from mobile</div>
  <div class="how-to-step">
    <div class="step-num">1</div>
    <div class="step-text">Run <code>run_all_agents.bat</code> on your PC to start all agents</div>
  </div>
  <div class="how-to-step">
    <div class="step-num">2</div>
    <div class="step-text">Find your PC IP address by running <code>ipconfig</code> in Command Prompt</div>
  </div>
  <div class="how-to-step">
    <div class="step-num">3</div>
    <div class="step-text">Connect your mobile to the same WiFi network as your PC</div>
  </div>
  <div class="how-to-step">
    <div class="step-num">4</div>
    <div class="step-text">Open mobile browser and go to <code>http://YOUR-PC-IP:8500</code> for this dashboard</div>
  </div>
  <div class="how-to-step">
    <div class="step-num">5</div>
    <div class="step-text">Tap any agent card to open it directly on your mobile</div>
  </div>
</div>

<div class="footer-note">ElderCare AI — Fetch.ai AgentVerse Hackathon</div>
""", unsafe_allow_html=True)
