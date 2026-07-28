"""
app.py - Main Streamlit Application
ElderCare AI – Family Notification Agent
Day 1 Single Agent Challenge
"""

import streamlit as st
import pandas as pd

from utils import (
    EMERGENCY_TYPES,
    RELATIONSHIP_OPTIONS,
    validate_fields,
    get_priority_badge,
    generate_report_text,
)
from notifications import (
    build_notification,
    simulate_notification_channels,
    add_to_history,
)

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ElderCare AI – Family Notification Agent",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS – Elder-friendly healthcare theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 16px; }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #C0392B;
        text-align: center;
        padding: 10px 0 4px 0;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 24px;
    }
    .alert-card {
        background: linear-gradient(135deg, #fff5f5, #ffe0e0);
        border-left: 6px solid #C0392B;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
    }
    .alert-card h3 { color: #C0392B; margin-bottom: 8px; }
    .alert-card p  { font-size: 1rem; margin: 4px 0; color: #333; }

    .summary-card {
        background: linear-gradient(135deg, #eafaf1, #d5f5e3);
        border-left: 6px solid #1E8449;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
    }
    .summary-card h3 { color: #1E8449; }
    .summary-card p  { font-size: 1rem; margin: 4px 0; color: #333; }

    div.stButton > button {
        font-size: 1.1rem;
        padding: 10px 28px;
        border-radius: 8px;
        font-weight: 600;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1A5276;
        border-bottom: 2px solid #AED6F1;
        padding-bottom: 6px;
        margin: 24px 0 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_notification" not in st.session_state:
    st.session_state.last_notification = None

# ──────────────────────────────────────────────
# Sidebar – Agent Info & Future Integrations
# ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/elderly-person.png", width=80)
    st.markdown("### 🏥 ElderCare AI")
    st.markdown("**Family Notification Agent**")
    st.markdown("---")
    st.markdown("#### 📊 Session Stats")
    st.metric("Notifications Sent", len(st.session_state.history))

    critical = sum(1 for h in st.session_state.history if h["Priority"] == "Critical")
    st.metric("Critical Alerts", critical)

    st.markdown("---")
    st.markdown("#### 🔗 ElderCare AI Agents")
    agents = [
        "💊 Medicine Reminder Agent",
        "📅 Appointment Booking Agent",
        "🚨 Emergency Detection Agent",
        "📋 Prescription Explainer Agent",
        "❤️ Health Monitoring Agent",
        "🎙️ Voice Companion Agent",
        "🥗 Diet Planning Agent",
        "🏃 Exercise Coach Agent",
        "🏥 Hospital Navigation Agent",
    ]
    for agent in agents:
        st.markdown(f"<small>{agent} *(coming soon)*</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("ElderCare AI · AgentVerse Hackathon · Day 1")

# ──────────────────────────────────────────────
# Home Page Header
# ──────────────────────────────────────────────
st.markdown('<div class="main-title">🚨 ElderCare AI – Family Notification Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">'
    'Automatically alerts family members during emergencies or important health events. '
    'Fast · Reliable · Elder-Friendly'
    '</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
col1.metric("👨‍👩‍👧 Families Protected", "1,240+")
col2.metric("🚨 Alerts Sent Today", "87")
col3.metric("⚡ Avg Response Time", "< 30 sec")

st.markdown("---")

# ──────────────────────────────────────────────
# Section 1 – Patient & Emergency Information Form
# ──────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Patient & Emergency Information</div>', unsafe_allow_html=True)

with st.form("emergency_form", clear_on_submit=False):
    col_a, col_b = st.columns(2)

    with col_a:
        patient_name = st.text_input("👤 Patient Name", placeholder="e.g. Rajamani Krishnan")
        age = st.number_input("🎂 Age", min_value=1, max_value=120, value=70, step=1)
        location = st.text_input("📍 Current Location", placeholder="e.g. 12, Anna Nagar, Chennai")
        emergency_type = st.selectbox("🚨 Emergency Type", [""] + EMERGENCY_TYPES)

    with col_b:
        contact_name = st.text_input("👥 Emergency Contact Name", placeholder="e.g. Karthik Rajamani")
        relationship = st.selectbox("🤝 Relationship", [""] + RELATIONSHIP_OPTIONS)
        contact_number = st.text_input("📞 Contact Number", placeholder="10-digit mobile number")

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚨 Send Notification", use_container_width=True)

# ──────────────────────────────────────────────
# Form Submission Handling
# ──────────────────────────────────────────────
if submitted:
    errors = validate_fields(
        patient_name, age, contact_name, relationship,
        contact_number, location, emergency_type
    )

    if errors:
        for err in errors:
            st.error(f"❌ {err}")
    else:
        # Build notification
        notification = build_notification(
            patient_name, age, emergency_type,
            location, contact_name, relationship, contact_number
        )
        st.session_state.last_notification = notification
        st.session_state.history = add_to_history(st.session_state.history, notification)

        st.success("✅ Emergency notification generated successfully!")

        # ── Alert Card ──────────────────────────────
        st.markdown('<div class="section-header">🚨 Emergency Notification</div>', unsafe_allow_html=True)
        priority_badge = get_priority_badge(notification["priority"])

        st.markdown(f"""
        <div class="alert-card">
            <h3>🚨 Emergency Alert – {notification['emergency_type']}</h3>
            <p>👤 <b>Patient:</b> {notification['patient_name']} &nbsp;|&nbsp; Age: {notification['age']}</p>
            <p>📍 <b>Location:</b> {notification['location']}</p>
            <p>🕐 <b>Date & Time:</b> {notification['date']} at {notification['time']}</p>
            <p>👥 <b>Contact:</b> {notification['contact_name']} ({notification['relationship']})</p>
            <p>📞 <b>Number:</b> {notification['contact_number']}</p>
            <p>{priority_badge} <b>Priority:</b> {notification['priority']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Notification Simulation ──────────────────
        st.markdown('<div class="section-header">📡 Notification Simulation</div>', unsafe_allow_html=True)
        channels = simulate_notification_channels(notification["priority"])
        for icon, msg, status in channels:
            if status == "success":
                st.success(f"{icon} {msg}")
            else:
                st.warning(f"{icon} ⚠️ {msg} (slight delay detected)")

        # ── Emergency Summary Card ───────────────────
        st.markdown('<div class="section-header">📊 Emergency Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="summary-card">
            <h3>✅ Notification Summary</h3>
            <p>👤 <b>Patient:</b> {notification['patient_name']}</p>
            <p>🚨 <b>Emergency:</b> {notification['emergency_type']}</p>
            <p>📍 <b>Location:</b> {notification['location']}</p>
            <p>👥 <b>Contact Person:</b> {notification['contact_name']}</p>
            <p>📞 <b>Contact Number:</b> {notification['contact_number']}</p>
            <p>{priority_badge} <b>Priority:</b> {notification['priority']}</p>
            <p>✅ <b>Status:</b> Sent</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Download Report ──────────────────────────
        report_text = generate_report_text(notification)
        st.download_button(
            label="📥 Download Emergency Report",
            data=report_text,
            file_name=f"emergency_report_{notification['date']}_{notification['time'].replace(':', '-')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ──────────────────────────────────────────────
# Section 2 – Notification History
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">📜 Notification History</div>', unsafe_allow_html=True)

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info(f"📊 Total notifications this session: **{len(st.session_state.history)}**")
else:
    st.info("📭 No notifications sent yet. Fill the form above to get started.")

# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>🏥 ElderCare AI · Family Notification Agent · "
    "AgentVerse Hackathon · Day 1 Single Agent Challenge</small></center>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Future Integration Points (DO NOT IMPLEMENT)
# ──────────────────────────────────────────────
# TODO: Medicine Reminder Agent  – show missed medicine schedule on sidebar
# TODO: Appointment Booking Agent – auto-book after High/Critical alert
# TODO: Emergency Detection Agent – replace form with live sensor feed
# TODO: Prescription Explainer Agent – attach prescription PDF to report
# TODO: Health Monitoring Agent   – live vitals dashboard on home page
# TODO: Voice Companion Agent     – add "Read Aloud" button for elder users
# TODO: Diet Planning Agent       – post-alert diet suggestion panel
# TODO: Exercise Coach Agent      – safe exercise plan after recovery
# TODO: Hospital Navigation Agent – map widget showing nearest hospital
