import textwrap
from pathlib import Path

import streamlit as st

from medicine_data import MedicineKnowledgeBase
from utils import build_summary_text, validate_form


class PrescriptionExplainerApp:
    """Main Streamlit application for explaining prescriptions in simple language."""

    def __init__(self) -> None:
        self.knowledge_base = MedicineKnowledgeBase()

    def run(self) -> None:
        self._set_page_style()
        self._render_home_page()
        self._render_form()

    def _set_page_style(self) -> None:
        st.markdown(
            """
            <style>
            .main {
                background: linear-gradient(135deg, #f7fcff 0%, #eef9f2 100%);
            }
            .stApp {
                color: #16324f;
            }
            .hero-card {
                background: linear-gradient(90deg, #0f766e 0%, #14b8a6 100%);
                padding: 1.4rem;
                border-radius: 16px;
                color: white;
                box-shadow: 0 8px 20px rgba(15, 118, 110, 0.18);
            }
            .summary-card {
                background: #f9fffc;
                border: 1px solid #bde8dd;
                border-radius: 14px;
                padding: 1rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _render_home_page(self) -> None:
        st.markdown(
            """
            <div class="hero-card">
                <h1>💊 ElderCare AI – Prescription Explainer Agent</h1>
                <p>This friendly app helps elderly patients understand medicines in simple, safe, and easy-to-read language.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.subheader("🧡 Why this helps")
        st.write(
            "Older adults can often feel overwhelmed by prescription instructions. This tool explains the purpose, timing, precautions, and common side effects in plain language."
        )

        col1, col2 = st.columns(2)
        with col1:
            st.info("📋 Enter the medicine details below to receive an easy explanation.")
        with col2:
            st.warning("⚠️ This app provides general information only and does not replace medical advice.")

    def _render_form(self) -> None:
        st.write("")
        st.subheader("📝 Patient Prescription Form")

        with st.form("prescription_form"):
            col1, col2 = st.columns(2)
            with col1:
                patient_name = st.text_input("Patient Name", placeholder="Enter patient name")
                age = st.text_input("Age", placeholder="e.g. 72")
                medicine_name = st.text_input("Medicine Name", placeholder="e.g. Paracetamol")
                dosage = st.text_input("Dosage", placeholder="e.g. 500 mg")
            with col2:
                frequency = st.text_input("Frequency", placeholder="e.g. Twice daily")
                food_relation = st.selectbox("Before/After Food", ["Before food", "After food", "With food", "Any time"])
                duration = st.text_input("Duration (Days)", placeholder="e.g. 5")
                medical_condition = st.text_input("Medical Condition", placeholder="e.g. Fever")

            submitted = st.form_submit_button("Explain Prescription")

        if submitted:
            errors = validate_form(
                patient_name=patient_name,
                age=age,
                medicine_name=medicine_name,
                dosage=dosage,
                frequency=frequency,
                food_relation=food_relation,
                duration=duration,
                medical_condition=medical_condition,
            )

            if errors:
                for error in errors:
                    st.error(error)
                return

            st.success("✅ Prescription details accepted. Preparing your easy-to-read explanation...")
            self._render_explanation(
                patient_name=patient_name,
                age=age,
                medicine_name=medicine_name,
                dosage=dosage,
                frequency=frequency,
                food_relation=food_relation,
                duration=duration,
                medical_condition=medical_condition,
            )

    def _render_explanation(
        self,
        patient_name: str,
        age: str,
        medicine_name: str,
        dosage: str,
        frequency: str,
        food_relation: str,
        duration: str,
        medical_condition: str,
    ) -> None:
        medicine = self.knowledge_base.get_medicine(medicine_name)
        if medicine is None:
            medicine = self.knowledge_base.get_generic_medicine(medicine_name)

        st.write("")
        st.subheader("📋 Medicine Information")
        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown(f"**Medicine:** {medicine.name}")
            st.markdown(f"**Purpose:** {medicine.purpose}")
            st.markdown(f"**What it treats:** {medicine.treats}")
            st.markdown(f"**How to take it:** {medicine.how_to_take.format(dosage=dosage, frequency=frequency)}")

        with info_col2:
            st.markdown(f"**Best time to take it:** {medicine.best_time}")
            st.markdown(f"**Before or after food:** {food_relation}")
            st.markdown(f"**Duration:** {duration} days")
            st.markdown(f"**Missed dose advice:** {medicine.missed_dose}")

        st.write("")
        with st.expander("⚠️ Precautions"):
            for item in medicine.precautions:
                st.write(f"- {item}")
            st.write("- Store the medicine in a cool, dry place away from direct sunlight.")
            st.write("- Keep medicines out of reach of children and pets.")
            st.write("- If you feel confused or unwell, contact your doctor or pharmacist.")

        st.write("")
        with st.expander("🩺 Possible Side Effects"):
            for item in medicine.side_effects:
                st.write(f"- {item}")
            st.warning("If side effects become severe, contact your doctor immediately.")

        st.write("")
        st.subheader("🧾 Prescription Summary")
        summary_text = build_summary_text(
            patient_name=patient_name,
            medicine_name=medicine.name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            purpose=medicine.purpose,
        )

        st.markdown(f"<div class='summary-card'>{summary_text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        st.write("")
        st.download_button(
            label="💾 Download Summary",
            data=summary_text.encode("utf-8"),
            file_name=f"{patient_name.replace(' ', '_').lower()}_summary.txt",
            mime="text/plain",
        )

        st.info("This explanation is general guidance only. It does not replace professional medical advice.")

        # Future integration point: Medicine Reminder Agent
        # Future integration point: Appointment Booking Agent
        # Future integration point: Emergency Detection Agent
        # Future integration point: Health Monitoring Agent
        # Future integration point: Family Notification Agent
        # Future integration point: Voice Companion Agent
        # Future integration point: Diet Planning Agent
        # Future integration point: Exercise Coach Agent
        # Future integration point: Hospital Navigation Agent


if __name__ == "__main__":
    app = PrescriptionExplainerApp()
    app.run()
