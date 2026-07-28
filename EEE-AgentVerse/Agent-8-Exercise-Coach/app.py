"""
app.py - Exercise Coach Agent
ElderCare AI – Day 1 Single Agent Challenge
"""

import streamlit as st
import pandas as pd
from exercise_data import CONDITIONS, FITNESS_LEVELS, WEEKLY_SCHEDULE, get_exercise_plan
from utils import validate_fields, generate_report_text

st.set_page_config(
    page_title="ElderCare AI – Exercise Coach Agent",
    page_icon="🏃",
    layout="wide",
)

st.markdown("""
<style>
    .main-title  { font-size:2.2rem; font-weight:800; color:#1A5276; text-align:center; padding:10px 0; }
    .sub-title   { font-size:1rem; color:#555; text-align:center; margin-bottom:20px; }
    .ex-card     { background:linear-gradient(135deg,#eaf4fb,#d6eaf8); border-left:6px solid #1A5276;
                   border-radius:12px; padding:20px 24px; margin:12px 0; }
    .ex-card h3  { color:#1A5276; }
    .warn-card   { background:linear-gradient(135deg,#fff9e6,#fef3cd); border-left:6px solid #F39C12;
                   border-radius:12px; padding:16px 20px; margin:10px 0; }
    .section-header { font-size:1.3rem; font-weight:700; color:#1A5276;
                      border-bottom:2px solid #AED6F1; padding-bottom:6px; margin:20px 0 10px 0; }
    div.stButton > button { font-size:1.05rem; padding:10px 24px; border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "exercise_history" not in st.session_state:
    st.session_state.exercise_history = []

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏃 ElderCare AI")
    st.markdown("**Exercise Coach Agent**")
    st.markdown("---")
    st.metric("Plans Generated", len(st.session_state.exercise_history))
    st.markdown("---")
    st.markdown("#### 📅 Weekly Schedule")
    for day, task in WEEKLY_SCHEDULE.items():
        st.markdown(f"<small><b>{day}</b>: {task}</small>", unsafe_allow_html=True)
    st.caption("ElderCare AI · AgentVerse Hackathon")

# ── Header ─────────────────────────────────────────────────
st.markdown('<div class="main-title">🏃 ElderCare AI – Exercise Coach Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Safe, personalized exercise plans for elderly based on health condition</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("🏋️ Exercise Plans", "5 Conditions")
c2.metric("⏱️ Daily Duration", "15–45 min")
c3.metric("🛡️ Safety First", "✅ Yes")

st.markdown("---")

# ── Form ───────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Patient Information</div>', unsafe_allow_html=True)

with st.form("exercise_form"):
    col1, col2 = st.columns(2)
    with col1:
        name          = st.text_input("👤 Patient Name", placeholder="e.g. Murugan")
        age           = st.number_input("🎂 Age", min_value=1, max_value=120, value=65)
    with col2:
        condition     = st.selectbox("🏥 Health Condition", [""] + CONDITIONS)
        fitness_level = st.selectbox("💪 Fitness Level", [""] + FITNESS_LEVELS)

    submitted = st.form_submit_button("🏃 Generate Exercise Plan", use_container_width=True)

# ── On Submit ──────────────────────────────────────────────
if submitted:
    errors = validate_fields(name, age, condition, fitness_level)
    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        plan = get_exercise_plan(condition)
        st.success("✅ Exercise plan generated successfully!")

        # Plan Overview
        st.markdown('<div class="section-header">🏋️ Exercise Plan Overview</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ex-card">
            <h3>🏃 {condition} – Exercise Plan</h3>
            <p>{plan['description']}</p>
            <p>⚡ <b>Intensity:</b> {plan['intensity']} &nbsp;|&nbsp; ⏱️ <b>Duration:</b> {plan['duration']}</p>
            <p>💡 <b>Tip:</b> {plan['tip']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Exercise Table
        st.markdown('<div class="section-header">💪 Daily Exercises</div>', unsafe_allow_html=True)
        ex_df = pd.DataFrame([
            {
                "Exercise": e["name"],
                "Duration/Sets": e.get("duration", e.get("sets", "—")),
                "Benefit": e["benefit"],
            }
            for e in plan["exercises"]
        ])
        st.dataframe(ex_df, use_container_width=True, hide_index=True)

        # Weekly Schedule
        st.markdown('<div class="section-header">📅 Weekly Schedule</div>', unsafe_allow_html=True)
        sched_df = pd.DataFrame(
            [{"Day": d, "Activity": t} for d, t in WEEKLY_SCHEDULE.items()]
        )
        st.dataframe(sched_df, use_container_width=True, hide_index=True)

        # Precautions
        st.markdown('<div class="section-header">⚠️ Safety Precautions</div>', unsafe_allow_html=True)
        for p in plan["precautions"]:
            st.warning(f"⚠️ {p}")

        # History
        st.session_state.exercise_history.append({
            "Patient": name, "Age": age,
            "Condition": condition, "Fitness Level": fitness_level,
            "Intensity": plan["intensity"],
        })

        # Download
        report_data = dict(name=name, age=age, condition=condition,
                           fitness_level=fitness_level, plan=plan,
                           schedule=WEEKLY_SCHEDULE)
        st.download_button(
            "📥 Download Exercise Plan",
            data=generate_report_text(report_data),
            file_name=f"exercise_plan_{name.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ── History ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">📜 Exercise Plan History</div>', unsafe_allow_html=True)
if st.session_state.exercise_history:
    st.dataframe(pd.DataFrame(st.session_state.exercise_history), use_container_width=True, hide_index=True)
else:
    st.info("📭 No exercise plans generated yet.")

st.markdown("---")
st.markdown("<center><small>🏃 ElderCare AI · Exercise Coach Agent · AgentVerse Hackathon</small></center>", unsafe_allow_html=True)
