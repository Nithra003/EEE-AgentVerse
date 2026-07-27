"""Simple Streamlit UI for the eldercare medicine reminder agent."""

from __future__ import annotations

import streamlit as st

from agents.medicine_reminder import MedicineReminderAgent


st.set_page_config(page_title="Eldercare Reminder Agent", page_icon="💊", layout="centered")
st.title("Eldercare Medicine Reminder Agent")
st.caption("Enter a reminder request and see the agent's response in JSON format.")

with st.form("reminder_form"):
    patient_name = st.text_input("Patient name", value="Evelyn")
    medicine_name = st.text_input("Medicine name", value="Vitamin D")
    dosage = st.text_input("Dosage", value="1 tablet")
    scheduled_time = st.text_input("Scheduled time", value="8:00 AM")
    patient_response = st.text_area(
        "Patient response (optional)",
        placeholder="Leave blank for a first reminder, or type a response such as 'Yes, I took it.'",
    )
    submitted = st.form_submit_button("Generate reminder")

if submitted:
    agent = MedicineReminderAgent()
    result = agent.generate_response(
        patient_name=patient_name,
        medicine_name=medicine_name,
        dosage=dosage,
        scheduled_time=scheduled_time,
        patient_response=patient_response or None,
    )
    st.success("Reminder generated")
    st.json(result)
