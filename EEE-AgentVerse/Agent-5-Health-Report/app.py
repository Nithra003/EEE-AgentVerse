"""Health Report Agent - Streamlit Web UI"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Health Report Agent", layout="centered")

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
    display: flex; align-items: center; gap: 1rem;
  }
  .top-bar-icon {
    width: 48px; height: 48px; border-radius: 12px;
    background: linear-gradient(135deg, #0c2a4a, #071828);
    border: 1px solid #38bdf8;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 20px rgba(56,189,248,0.25);
    flex-shrink: 0;
  }
  .top-bar-title { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; }
  .top-bar-sub   { font-size: 0.78rem; color: #556677; margin-top: 0.2rem; }

  .card {
    background: #0d1526;
    border: 1px solid #1a2840;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    animation: fadeIn 0.4s ease;
  }

  .card-title {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: #38bdf8; margin-bottom: 0.9rem;
  }

  .metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  @media (max-width: 480px) {
    .metric-grid { grid-template-columns: repeat(2, 1fr); }
  }

  .metric-card {
    background: #0a0f1a;
    border: 1px solid #1a2840;
    border-radius: 12px;
    padding: 0.9rem 0.7rem;
    text-align: center;
  }

  .metric-label { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #445566; margin-bottom: 0.3rem; }
  .metric-value { font-size: 1rem; font-weight: 700; color: #dde8f5; }
  .metric-status { font-size: 0.65rem; margin-top: 0.2rem; }

  .status-normal   { color: #4ade80; }
  .status-high     { color: #f87171; }
  .status-low      { color: #fbbf24; }
  .status-critical { color: #f87171; font-weight: 700; }
  .status-fever    { color: #fb923c; }
  .status-fair     { color: #fbbf24; }
  .status-poor     { color: #f87171; }
  .status-active   { color: #4ade80; }

  .risk-low      { color: #4ade80; }
  .risk-medium   { color: #fbbf24; }
  .risk-high     { color: #f87171; }

  .detail-row {
    display: flex; justify-content: space-between;
    padding: 0.5rem 0; border-bottom: 1px solid #0d1526;
    font-size: 0.82rem;
  }
  .detail-key   { color: #445566; }
  .detail-value { color: #dde8f5; font-weight: 600; }

  .reco-item {
    padding: 0.4rem 0; font-size: 0.82rem; color: #7a8fa8;
    border-bottom: 1px solid #0d1526;
  }
  .reco-item::before { content: "— "; color: #38bdf8; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
""", unsafe_allow_html=True)

from models import HealthData, HealthMetricStatus, HealthReport
from health_report_agent import HealthReportAgent

st.markdown("""
<div class="top-bar">
  <div class="top-bar-icon">📊</div>
  <div>
    <div class="top-bar-title">Health Report Agent</div>
    <div class="top-bar-sub">ElderCare AI — Wearable data analysis and risk classification</div>
  </div>
</div>
""", unsafe_allow_html=True)

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
        import asyncio
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
