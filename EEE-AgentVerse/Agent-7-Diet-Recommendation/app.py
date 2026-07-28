"""
app.py - Diet Recommendation Agent
ElderCare AI – Day 1 Single Agent Challenge
"""

import streamlit as st
import pandas as pd
from diet_data import CONDITIONS, calculate_bmi, get_diet_plan
from utils import validate_fields, generate_report_text

st.set_page_config(
    page_title="ElderCare AI – Diet Recommendation Agent",
    page_icon="🥗",
    layout="wide",
)

st.markdown("""
<style>
    .main-title { font-size:2.2rem; font-weight:800; color:#1E8449; text-align:center; padding:10px 0; }
    .sub-title  { font-size:1rem; color:#555; text-align:center; margin-bottom:20px; }
    .diet-card  { background:linear-gradient(135deg,#eafaf1,#d5f5e3); border-left:6px solid #1E8449;
                  border-radius:12px; padding:20px 24px; margin:12px 0; }
    .diet-card h3 { color:#1E8449; }
    .warn-card  { background:linear-gradient(135deg,#fff9e6,#fef3cd); border-left:6px solid #F39C12;
                  border-radius:12px; padding:20px 24px; margin:12px 0; }
    .section-header { font-size:1.3rem; font-weight:700; color:#1A5276;
                      border-bottom:2px solid #AED6F1; padding-bottom:6px; margin:20px 0 10px 0; }
    div.stButton > button { font-size:1.05rem; padding:10px 24px; border-radius:8px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
if "diet_history" not in st.session_state:
    st.session_state.diet_history = []

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 ElderCare AI")
    st.markdown("**Diet Recommendation Agent**")
    st.markdown("---")
    st.metric("Plans Generated", len(st.session_state.diet_history))
    st.markdown("---")
    st.markdown("#### 🔗 ElderCare AI Agents")
    for a in ["💊 Medicine Reminder","🚨 Emergency Detection","📅 Appointment Booking",
              "📋 Prescription Explainer","📊 Health Report","👨‍👩‍👧 Family Notifier",
              "🏃 Exercise Coach","😊 Mood Companion","🎙️ Voice Assistant"]:
        st.markdown(f"<small>{a} *(coming soon)*</small>", unsafe_allow_html=True)
    st.caption("ElderCare AI · AgentVerse Hackathon")

# ── Header ─────────────────────────────────────────────────
st.markdown('<div class="main-title">🥗 ElderCare AI – Diet Recommendation Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Personalized diet plans for elderly based on health conditions & BMI</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("🥗 Diet Plans", "5 Conditions")
c2.metric("🍽️ Meal Slots", "5 Per Day")
c3.metric("👴 Elder-Friendly", "✅ Yes")

st.markdown("---")

# ── Form ───────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Patient Information</div>', unsafe_allow_html=True)

with st.form("diet_form"):
    col1, col2 = st.columns(2)
    with col1:
        name   = st.text_input("👤 Patient Name", placeholder="e.g. Rajamani")
        age    = st.number_input("🎂 Age", min_value=1, max_value=120, value=65)
        weight = st.number_input("⚖️ Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5)
    with col2:
        gender    = st.selectbox("⚧ Gender", ["", "Male", "Female", "Other"])
        height    = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=165.0, step=0.5)
        condition = st.selectbox("🏥 Health Condition", [""] + CONDITIONS)

    submitted = st.form_submit_button("🥗 Generate Diet Plan", use_container_width=True)

# ── On Submit ──────────────────────────────────────────────
if submitted:
    errors = validate_fields(name, age, weight, height, condition, gender)
    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        bmi, bmi_cat = calculate_bmi(weight, height)
        plan = get_diet_plan(condition)

        st.success("✅ Diet plan generated successfully!")

        # BMI Card
        st.markdown('<div class="section-header">📊 BMI Analysis</div>', unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        b1.metric("BMI Score", bmi)
        b2.metric("Category", bmi_cat)
        b3.metric("Condition", condition)

        bmi_color = {"Normal": "🟢", "Underweight": "🟡", "Overweight": "🟠", "Obese": "🔴"}.get(bmi_cat, "⚪")
        if bmi_cat == "Normal":
            st.success(f"{bmi_color} BMI is Normal – Great! Keep maintaining a healthy lifestyle.")
        elif bmi_cat == "Underweight":
            st.warning(f"{bmi_color} BMI is low – Focus on nutrient-rich foods to gain healthy weight.")
        else:
            st.warning(f"{bmi_color} BMI is {bmi_cat} – Follow the diet plan carefully.")

        # Diet Plan Card
        st.markdown('<div class="section-header">🍽️ Personalized Diet Plan</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="diet-card">
            <h3>🥗 Diet Plan for {condition}</h3>
            <p>{plan['description']}</p>
            <p>💧 <b>Water Intake:</b> {plan['water_intake']}</p>
            <p>💡 <b>Tip:</b> {plan['tip']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Meal Plan Table
        st.markdown('<div class="section-header">🕐 Daily Meal Schedule</div>', unsafe_allow_html=True)
        meal_df = pd.DataFrame(
            [{"Meal Time": k, "Recommended Food": v} for k, v in plan["meal_plan"].items()]
        )
        st.dataframe(meal_df, use_container_width=True, hide_index=True)

        # Foods
        col_eat, col_avoid = st.columns(2)
        with col_eat:
            st.markdown("#### ✅ Foods to Eat")
            for f in plan["foods_to_eat"]:
                st.success(f"✓ {f}")
        with col_avoid:
            st.markdown("#### ❌ Foods to Avoid")
            for f in plan["foods_to_avoid"]:
                st.error(f"✗ {f}")

        # History
        st.session_state.diet_history.append({
            "Patient": name, "Age": age, "Condition": condition,
            "BMI": bmi, "Category": bmi_cat,
        })

        # Download
        report_data = dict(name=name, age=age, gender=gender, weight=weight,
                           height=height, bmi=bmi, bmi_category=bmi_cat,
                           condition=condition, plan=plan)
        st.download_button(
            "📥 Download Diet Report",
            data=generate_report_text(report_data),
            file_name=f"diet_report_{name.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ── History ────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-header">📜 Diet Plan History</div>', unsafe_allow_html=True)
if st.session_state.diet_history:
    st.dataframe(pd.DataFrame(st.session_state.diet_history), use_container_width=True, hide_index=True)
else:
    st.info("📭 No diet plans generated yet.")

st.markdown("---")
st.markdown("<center><small>🥗 ElderCare AI · Diet Recommendation Agent · AgentVerse Hackathon</small></center>", unsafe_allow_html=True)
