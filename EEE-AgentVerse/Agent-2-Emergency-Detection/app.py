"""Emergency Detection Agent - Live Web Dashboard"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
import time
from datetime import datetime
import streamlit as st
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Emergency Detection Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="emergency")
agent_header(
    title="🚨 Emergency Detection Agent",
    subtitle="ElderCare AI — Real-time fall and emergency monitoring",
    accent="#f87171",
)

# --- Agent Logic ---

def simulate_sensor():
    """Simulate wearable sensor data. 30% chance of emergency."""
    if random.random() < 0.3:
        return {"movement": "none", "posture": "lying", "time_on_ground": random.randint(21, 60)}
    return {
        "movement": random.choice(["none", "low", "high"]),
        "posture":  random.choice(["standing", "sitting"]),
        "time_on_ground": random.randint(0, 10),
    }

def detect_fall(sensor: dict) -> bool:
    return (
        sensor["posture"] == "lying"
        and sensor["movement"] == "none"
        and sensor["time_on_ground"] > 20
    )

# --- Session State ---
for _k, _v in {
    "log": [], "reading_count": 0,
    "last_sensor": None, "last_emergency": False, "monitoring": False,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# --- Controls ---
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    if st.button("Take Reading", use_container_width=True, type="primary"):
        sensor       = simulate_sensor()
        is_emergency = detect_fall(sensor)
        ts           = datetime.now().strftime("%H:%M:%S")
        st.session_state.reading_count += 1
        st.session_state.last_sensor    = sensor
        st.session_state.last_emergency = is_emergency
        entry = {
            "time": ts, "reading": st.session_state.reading_count,
            "movement": sensor["movement"], "posture": sensor["posture"],
            "time_on_ground": sensor["time_on_ground"], "emergency": is_emergency,
        }
        st.session_state.log = [entry] + st.session_state.log[:29]

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

# --- Auto Monitor (non-blocking: timestamp-based) ---
if st.session_state.monitoring:
    import time as _time
    last_auto = st.session_state.get("_last_auto_ts", 0)
    now_ts = _time.monotonic()
    if now_ts - last_auto >= 3.0:
        st.session_state["_last_auto_ts"] = now_ts
        sensor       = simulate_sensor()
        is_emergency = detect_fall(sensor)
        ts           = datetime.now().strftime("%H:%M:%S")
        st.session_state.reading_count += 1
        st.session_state.last_sensor    = sensor
        st.session_state.last_emergency = is_emergency
        st.session_state.log = [{
            "time": ts, "reading": st.session_state.reading_count,
            "movement": sensor["movement"], "posture": sensor["posture"],
            "time_on_ground": sensor["time_on_ground"], "emergency": is_emergency,
        }] + st.session_state.log[:29]
    # Use st.rerun with a short sleep only to avoid 100% CPU spin
    _time.sleep(0.5)
    st.rerun()
