"""
app.py - Mood Companion Agent
ElderCare AI – Day 1 Single Agent Challenge
"""

import random
import streamlit as st
import pandas as pd
from datetime import datetime
from responses import MOODS, DAILY_AFFIRMATIONS, BREATHING_EXERCISE, get_mood_response
from utils import validate_fields, generate_report_text

st.set_page_config(
    page_title="ElderCare AI – Mood Companion Agent",
    page_icon="😊",
    layout="wide",
)

st.markdown("""
<style>
    .main-title  { font-size:2.2rem; font-weight:800; color:#6C3483; text-align:center; padding:10px 0; }
    .sub-title   { font-size:1rem; color:#555; text-align:center; margin-bottom:20px; }
    .mood-card   { border-radius:14px; padding:22px 26px; margin:14px 0; }
    .affirmation { background:linear-gradient(135deg,#f5eef8,#e8daef); border-left:6px solid #6C3483;
                   border-radius:12px; padding:18px 22px; margin:12px 0; font-size:1.1rem; }
    .breathing   { background:linear-gradient(135deg,#eafaf1,#d5f5e3); border-left:6px solid #1E8449;
                   border-radius:12px; padding:18px 22px; margin:12px 0; }
    .section-header { font-size:1.3rem; font-weight:700; color:#6C3483;
                      border-bottom:2px solid #D7BDE2; padding-bottom:6px; margin:20px 0 10px 0; }
    div.stButton > button { font-size:1.05rem; padding:10px 24px; border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "mood_history" not in st.session_state:
    st.session_state.mood_history = []
if "daily_affirmation" not in st.session_state:
    st.session_state.daily_affirmation = random.choice(DAILY_AFFIRMATIONS)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 😊 ElderCare AI")
    st.markdown("**Mood Companion Agent**")
    st.markdown("---")
    st.metric("Check-ins Today", len(st.session_state.mood_history))
    st.markdown("---")
    st.markdown("#### 💬 Today's Affirmation")
    st.info(f'"{st.session_state.daily_affirmation}"')
    st.markdown("---")
    st.markdown("#### 🧘 Quick Breathing")
    st.markdown(f"**{BREATHING_EXERCISE['name']}**")
    for i, step in enumerate(BREATHING_EXERCISE["steps"], 1):
        st.markdown(f"<small>{i}. {step}</small>", unsafe_allow_html=True)
    st.caption("ElderCare AI · AgentVerse Hackathon")

# ── Header ─────────────────────────────────────────────────
st.markdown('<div class="main-title">😊 ElderCare AI – Mood Companion Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Your caring companion for emotional wellness and daily positivity</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("😊 Mood Options", "6 Moods")
c2.metric("🎯 Activities", "5 Per Mood")
c3.metric("💬 Affirmations", "Daily")

st.markdown("---")

# ── Daily Affirmation Banner ───────────────────────────────
st.markdown(f"""
<div class="affirmation">
    💬 <b>Today's Affirmation:</b><br>
    <i>"{st.session_state.daily_affirmation}"</i>
</div>
""", unsafe_allow_html=True)

# ── Form ───────────────────────────────────────────────────
st.markdown('<div class="section-header">🌟 How Are You Feeling Today?</div>', unsafe_allow_html=True)

with st.form("mood_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Your Name", placeholder="e.g. Kamala Paati")
        age  = st.number_input("🎂 Age", min_value=1, max_value=120, value=68)
    with col2:
        mood = st.selectbox("💭 How are you feeling right now?", [""] + MOODS)
        note = st.text_area("📝 Want to share anything? (optional)", placeholder="Write how your day is going...", height=80)

    submitted = st.form_submit_button("💙 Get Support & Activities", use_container_width=True)

# ── On Submit ──────────────────────────────────────────────
if submitted:
    errors = validate_fields(name, age, mood)
    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        response = get_mood_response(mood)
        st.success(f"💙 Hello {name}! Here's your personalised support.")

        # Mood Response Card
        st.markdown('<div class="section-header">💬 Your Mood Response</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="mood-card" style="background:linear-gradient(135deg,#f8f9fa,#e9ecef);
             border-left:6px solid {response['color']};">
            <h3 style="color:{response['color']};">{mood}</h3>
            <p style="font-size:1.1rem;">{response['message']}</p>
            <p>💡 <b>Tip:</b> {response['tip']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Affirmation
        st.markdown(f"""
        <div class="affirmation">
            💬 <b>A message for you, {name}:</b><br>
            <i>"{response['affirmation']}"</i>
        </div>
        """, unsafe_allow_html=True)

        # Activities
        st.markdown('<div class="section-header">🎯 Suggested Activities</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, activity in enumerate(response["activities"]):
            cols[i % 2].info(activity)

        # Breathing Exercise
        st.markdown('<div class="section-header">🧘 Breathing Exercise</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="breathing">
            <b>🌬️ {BREATHING_EXERCISE['name']}</b><br>
            <small>{BREATHING_EXERCISE['benefit']}</small>
        </div>
        """, unsafe_allow_html=True)
        for i, step in enumerate(BREATHING_EXERCISE["steps"], 1):
            st.markdown(f"**{i}.** {step}")

        # Log to history
        st.session_state.mood_history.append({
            "Name": name,
            "Age": age,
            "Mood": mood,
            "Note": note if note else "—",
            "Time": datetime.now().strftime("%H:%M:%S"),
        })

        # Download
        report_data = dict(name=name, age=age, mood=mood, response=response)
        st.download_button(
            "📥 Download Mood Report",
            data=generate_report_text(report_data),
            file_name=f"mood_report_{name.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ── Mood History ───────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">📜 Today\'s Mood Log</div>', unsafe_allow_html=True)
if st.session_state.mood_history:
    st.dataframe(pd.DataFrame(st.session_state.mood_history), use_container_width=True, hide_index=True)
else:
    st.info("📭 No mood check-ins yet. Share how you feel above! 😊")

st.markdown("---")
st.markdown("<center><small>😊 ElderCare AI · Mood Companion Agent · AgentVerse Hackathon</small></center>", unsafe_allow_html=True)
