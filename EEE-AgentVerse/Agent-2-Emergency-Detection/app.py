"""Emergency Detection Agent - Live Web Dashboard"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
import time
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Emergency Detection Agent", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
    background: #060b14 !important;
    font-family: 'Inter', sans-serif;
  }
  [data-testid="stHeader"], footer, #MainMenu { display: none; }

  .top-bar {
    background: linear-gradient(135deg, #0d1a2e, #0a1220);
    border: 1px solid #1a2840;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .top-bar-icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #7f1d1d, #450a0a);
    border: 1px solid #f87171;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 20px rgba(248,113,113,0.3);
    flex-shrink: 0;
  }

  .top-bar-title { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
  .top-bar-sub   { font-size: 0.78rem; color: #556677; margin-top: 0.2rem; }

  .status-safe {
    background: linear-gradient(135deg, #052e16, #041a0e);
    border: 1px solid #166534;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    animation: fadeIn 0.4s ease;
  }

  .status-emergency {
    background: linear-gradient(135deg, #450a0a, #2d0606);
    border: 2px solid #f87171;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    animation: emergencyPulse 1s ease infinite;
  }

  .status-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }

  .status-safe .status-label   { color: #4ade80; }
  .status-emergency .status-label { color: #f87171; }

  .status-text-safe      { font-size: 1.3rem; font-weight: 700; color: #4ade80; }
  .status-text-emergency { font-size: 1.3rem; font-weight: 700; color: #f87171; }

  .sensor-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .sensor-card {
    background: #0d1526;
    border: 1px solid #1a2840;
    border-radius: 12px;
    padding: 1rem 0.8rem;
    text-align: center;
    animation: fadeIn 0.4s ease;
  }

  .sensor-label {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #445566;
    margin-bottom: 0.4rem;
  }

  .sensor-value {
    font-size: 1rem;
    font-weight: 700;
    color: #dde8f5;
  }

  .sensor-value.danger { color: #f87171; }
  .sensor-value.warn   { color: #fbbf24; }
  .sensor-value.ok     { color: #4ade80; }

  .log-container {
    background: #0a0f1a;
    border: 1px solid #1a2840;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    max-height: 260px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
  }

  .log-entry {
    padding: 0.3rem 0;
    border-bottom: 1px solid #0d1526;
    animation: fadeIn 0.3s ease;
  }

  .log-time  { color: #334455; margin-right: 0.5rem; }
  .log-safe  { color: #4ade80; }
  .log-alert { color: #f87171; font-weight: 600; }
  .log-info  { color: #60a5fa; }

  .reading-counter {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #0d1526;
    border: 1px solid #1a2840;
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.72rem;
    color: #556677;
    margin-bottom: 1rem;
  }

  .pulse-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse 1.5s infinite;
  }

  .pulse-dot.red { background: #f87171; animation: pulseRed 0.6s infinite; }

  .alert-banner {
    background: linear-gradient(135deg, #7f1d1d, #450a0a);
    border: 2px solid #f87171;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    text-align: center;
    animation: emergencyPulse 0.8s ease infinite;
  }

  .alert-banner-title { font-size: 1.1rem; font-weight: 700; color: #fca5a5; letter-spacing: 0.05em; }
  .alert-banner-sub   { font-size: 0.82rem; color: #f87171; margin-top: 0.3rem; }

  .detail-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #0d1526;
    font-size: 0.82rem;
  }
  .detail-key   { color: #445566; }
  .detail-value { color: #dde8f5; font-weight: 600; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }
    50%       { box-shadow: 0 0 0 5px rgba(34,197,94,0); }
  }

  @keyframes pulseRed {
    0%, 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0.6); }
    50%       { box-shadow: 0 0 0 6px rgba(248,113,113,0); }
  }

  @keyframes emergencyPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0.3); }
    50%       { box-shadow: 0 0 20px rgba(248,113,113,0.2); }
  }
</style>
""", unsafe_allow_html=True)

# --- Agent Logic ---

def simulate_sensor():
    is_emergency = random.random() < 0.3
    if is_emergency:
        return {"movement": "none", "posture": "lying", "time_on_ground": random.randint(21, 60)}
    return {
        "movement": random.choice(["none", "low", "high"]),
        "posture": random.choice(["standing", "sitting"]),
        "time_on_ground": random.randint(0, 10),
    }

def detect_fall(sensor):
    return (
        sensor["posture"] == "lying"
        and sensor["movement"] == "none"
        and sensor["time_on_ground"] > 20
    )

# --- Session State ---
if "log" not in st.session_state:
    st.session_state.log = []
if "reading_count" not in st.session_state:
    st.session_state.reading_count = 0
if "last_sensor" not in st.session_state:
    st.session_state.last_sensor = None
if "last_emergency" not in st.session_state:
    st.session_state.last_emergency = False
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# --- Header ---
st.markdown("""
<div class="top-bar">
  <div class="top-bar-icon">🚨</div>
  <div>
    <div class="top-bar-title">Emergency Detection Agent</div>
    <div class="top-bar-sub">ElderCare AI — Real-time fall and emergency monitoring</div>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Controls ---
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    if st.button("Take Reading", use_container_width=True, type="primary"):
        sensor = simulate_sensor()
        is_emergency = detect_fall(sensor)
        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.reading_count += 1
        st.session_state.last_sensor = sensor
        st.session_state.last_emergency = is_emergency

        log_entry = {
            "time": ts,
            "reading": st.session_state.reading_count,
            "movement": sensor["movement"],
            "posture": sensor["posture"],
            "time_on_ground": sensor["time_on_ground"],
            "emergency": is_emergency,
        }
        st.session_state.log.insert(0, log_entry)
        if len(st.session_state.log) > 30:
            st.session_state.log = st.session_state.log[:30]

with col2:
    auto = st.toggle("Auto Monitor", value=st.session_state.monitoring)
    st.session_state.monitoring = auto

with col3:
    if st.button("Clear Log", use_container_width=True):
        st.session_state.log = []
        st.session_state.reading_count = 0
        st.session_state.last_sensor = None
        st.session_state.last_emergency = False
        st.rerun()

# --- Reading Counter ---
dot_class = "pulse-dot red" if st.session_state.last_emergency else "pulse-dot"
st.markdown(f"""
<div class="reading-counter">
  <div class="{dot_class}"></div>
  Reading #{st.session_state.reading_count} &nbsp;|&nbsp; Person: John Doe &nbsp;|&nbsp; Location: Living Room
</div>
""", unsafe_allow_html=True)

# --- Current Status ---
if st.session_state.last_sensor:
    sensor = st.session_state.last_sensor
    is_em = st.session_state.last_emergency

    if is_em:
        st.markdown("""
        <div class="alert-banner">
          <div class="alert-banner-title">FALL DETECTED — EMERGENCY PROTOCOL ACTIVE</div>
          <div class="alert-banner-sub">Contacting emergency services and family members</div>
        </div>
        """, unsafe_allow_html=True)

    status_class = "status-emergency" if is_em else "status-safe"
    status_text_class = "status-text-emergency" if is_em else "status-text-safe"
    status_label = "EMERGENCY" if is_em else "SAFE"
    status_display = "Fall Detected" if is_em else "No Emergency"

    st.markdown(f"""
    <div class="{status_class}">
      <div class="status-label">{status_label}</div>
      <div class="{status_text_class}">{status_display}</div>
      <div style="margin-top:0.8rem;">
        <div class="detail-row"><span class="detail-key">Person</span><span class="detail-value">John Doe</span></div>
        <div class="detail-row"><span class="detail-key">Location</span><span class="detail-value">Living Room</span></div>
        <div class="detail-row"><span class="detail-key">Risk Level</span><span class="detail-value">{"HIGH" if is_em else "LOW"}</span></div>
        <div class="detail-row"><span class="detail-key">Time</span><span class="detail-value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Sensor cards
    m_class = "danger" if sensor["movement"] == "none" and is_em else "ok"
    p_class = "danger" if sensor["posture"] == "lying" and is_em else "ok"
    t_class = "danger" if sensor["time_on_ground"] > 20 else ("warn" if sensor["time_on_ground"] > 10 else "ok")

    st.markdown(f"""
    <div class="sensor-grid">
      <div class="sensor-card">
        <div class="sensor-label">Movement</div>
        <div class="sensor-value {m_class}">{sensor['movement'].upper()}</div>
      </div>
      <div class="sensor-card">
        <div class="sensor-label">Posture</div>
        <div class="sensor-value {p_class}">{sensor['posture'].upper()}</div>
      </div>
      <div class="sensor-card">
        <div class="sensor-label">On Ground</div>
        <div class="sensor-value {t_class}">{sensor['time_on_ground']}s</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if is_em:
        st.markdown("""
        <div style="background:#0d1526;border:1px solid #1a2840;border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1rem;">
          <div style="font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#f87171;margin-bottom:0.8rem;">Emergency Response Actions</div>
          <div class="detail-row"><span class="detail-key">Emergency Contact 1</span><span class="detail-value" style="color:#4ade80;">Jane Doe (Daughter) — Notified</span></div>
          <div class="detail-row"><span class="detail-key">Emergency Contact 2</span><span class="detail-value" style="color:#4ade80;">St. Mary's Hospital — Notified</span></div>
          <div class="detail-row"><span class="detail-key">Ambulance</span><span class="detail-value" style="color:#4ade80;">Dispatched — ETA 8 min</span></div>
          <div class="detail-row"><span class="detail-key">Incident Log</span><span class="detail-value" style="color:#4ade80;">Recorded</span></div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-safe">
      <div class="status-label">WAITING</div>
      <div class="status-text-safe">Press "Take Reading" to start monitoring</div>
    </div>
    """, unsafe_allow_html=True)

# --- Log ---
st.markdown("""
<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:#445566;margin-bottom:0.6rem;">
  Sensor Log
</div>
""", unsafe_allow_html=True)

if st.session_state.log:
    log_html = '<div class="log-container">'
    for entry in st.session_state.log:
        cls = "log-alert" if entry["emergency"] else "log-safe"
        status_str = "EMERGENCY — Fall Detected" if entry["emergency"] else "Safe"
        log_html += (
            f'<div class="log-entry">'
            f'<span class="log-time">{entry["time"]}</span>'
            f'<span class="log-info">#{entry["reading"]}</span> '
            f'<span style="color:#445566;"> | {entry["posture"]} | {entry["movement"]} | {entry["time_on_ground"]}s | </span>'
            f'<span class="{cls}">{status_str}</span>'
            f'</div>'
        )
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)
else:
    st.markdown('<div class="log-container"><span style="color:#334455;">No readings yet. Press Take Reading to begin.</span></div>', unsafe_allow_html=True)

# --- Auto Monitor ---
if st.session_state.monitoring:
    time.sleep(5)
    sensor = simulate_sensor()
    is_emergency = detect_fall(sensor)
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.reading_count += 1
    st.session_state.last_sensor = sensor
    st.session_state.last_emergency = is_emergency
    st.session_state.log.insert(0, {
        "time": ts,
        "reading": st.session_state.reading_count,
        "movement": sensor["movement"],
        "posture": sensor["posture"],
        "time_on_ground": sensor["time_on_ground"],
        "emergency": is_emergency,
    })
    if len(st.session_state.log) > 30:
        st.session_state.log = st.session_state.log[:30]
    st.rerun()
