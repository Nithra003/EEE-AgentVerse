"""Health Report Agent - Streamlit Web UI"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import streamlit as st
from datetime import datetime
from health_report_agent import HealthReportAgent
from shared.agent_bridge import health_report_to_diet_exercise
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="Health Report Agent", layout="wide")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="health")
agent_header(
    title="📊 Health Report Agent",
    subtitle="ElderCare AI — Wearable data analysis and risk classification",
    accent="#38bdf8",
)

# --- Input Form ---
with st.expander("Enter Patient Health Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name", value="John")
        age = st.number_input("Age", min_value=1, max_value=120, value=72)
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=20, max_value=250, value=108)
        spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=91)
        body_temp = st.number_input("Body Temperature (C)", min_value=34.0, max_value=42.0, value=38.4, step=0.1)
    with col2:
        blood_pressure = st.text_input("Blood Pressure (sys/dia)", value="150/95")
        steps = st.number_input("Steps Today", min_value=0, max_value=50000, value=1800)
        sleep_hours = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, value=5.0, step=0.5)

    generate = st.button("Generate Health Report", use_container_width=True, type="primary")

if generate or "report" in st.session_state:
    if generate:
        agent = HealthReportAgent()
        payload = {
            "patient_name": patient_name,
            "age": int(age),
            "heart_rate": int(heart_rate),
            "spo2": int(spo2),
            "body_temperature": float(body_temp),
            "blood_pressure": blood_pressure,
            "steps": int(steps),
            "sleep_hours": float(sleep_hours),
            "timestamp": datetime.utcnow().isoformat(),
        }
        report = asyncio.run(agent.receive_health_data(payload))
        st.session_state.report = report
        health_report_to_diet_exercise(
            patient_name=report.patient_name,
            age=report.age,
            condition=report.overall_status,
            risk_level=report.risk_level,
            recommendations=report.recommendations,
        )

    report = st.session_state.report

    # Risk badge color
    risk_class = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(report.risk_level, "risk-low")

    st.markdown(f"""
    <div class="card">
      <div class="card-title">Overall Status</div>
      <div class="detail-row"><span class="detail-key">Patient</span><span class="detail-value">{report.patient_name}, Age {report.age}</span></div>
      <div class="detail-row"><span class="detail-key">Health Status</span><span class="detail-value">{report.overall_status}</span></div>
      <div class="detail-row"><span class="detail-key">Risk Level</span><span class="detail-value {risk_class}">{report.risk_level}</span></div>
      <div class="detail-row"><span class="detail-key">Report ID</span><span class="detail-value">{report.report_id}</span></div>
      <div class="detail-row" style="border:none;"><span class="detail-key">Generated</span><span class="detail-value">{report.timestamp.strftime("%Y-%m-%d %I:%M %p")}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    status_color_map = {
        "Normal": "status-normal", "High": "status-high", "Low": "status-low",
        "Critical": "status-critical", "Fever": "status-fever", "Fair": "status-fair",
        "Poor": "status-poor", "Active": "status-active", "Low Activity": "status-low",
    }

    metric_cards = ""
    for label, value in report.metrics.items():
        analysis_val = report.analysis.get(label, "")
        color_class = status_color_map.get(analysis_val, "status-normal")
        metric_cards += f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-status {color_class}">{analysis_val}</div>
        </div>
        """

    st.markdown(f"""
    <div class="card">
      <div class="card-title">Health Metrics</div>
      <div class="metric-grid">{metric_cards}</div>
    </div>
    """, unsafe_allow_html=True)

    reco_html = "".join(f'<div class="reco-item">{r}</div>' for r in report.recommendations)
    st.markdown(f"""
    <div class="card">
      <div class="card-title">Recommendations</div>
      {reco_html}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
      <div class="card-title">Summary</div>
      <div style="font-size:0.85rem;color:#7a8fa8;line-height:1.6;">{report.summary}</div>
    </div>
    """, unsafe_allow_html=True)
