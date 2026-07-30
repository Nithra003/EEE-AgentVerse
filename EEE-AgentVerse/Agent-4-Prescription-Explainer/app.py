"""Prescription Explainer Agent — Image Upload + OCR + Manual Entry"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.agent_bridge import prescription_to_reminder
from shared.ui_components import init_theme, sidebar_nav, agent_header, language_selector, tts_button
from shared.ui_theme import inject

import streamlit as st
from datetime import datetime
from utils import build_summary_text
from gemini_helper import ask_gemini
from ocr_engine import extract_prescription

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "prescription_history.json")

def _load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def _save_history(records: list):
    with open(HISTORY_FILE, "w") as f:
        json.dump(records, f, indent=2)

def extract_prescription_from_image(image_bytes: bytes) -> dict:
    """Run multi-engine OCR pipeline (EasyOCR → Tesseract) with OpenCV preprocessing."""
    result = extract_prescription(image_bytes)
    if result.get("error"):
        return result
    f = result["fields"]
    # Normalise to the shape the rest of app.py expects
    medicines = [
        {
            "name":             med,
            "dosage":           f["dosage"][i] if i < len(f["dosage"]) else "",
            "frequency":        f["frequency"][i] if i < len(f["frequency"]) else "",
            "duration":         f["duration"][i] if i < len(f["duration"]) else "",
            "food_instruction": f["instructions"][i] if i < len(f["instructions"]) else "",
            "notes":            "",
        }
        for i, med in enumerate(f["medicines"])
    ]
    return {
        "patient_name": f["patient"],
        "doctor_name":  f["doctor"],
        "hospital":     f["hospital"],
        "date":         f["date"],
        "diagnosis":    "",
        "medicines":    medicines,
        # OCR metadata
        "_confidence":  result["confidence"],
        "_ocr_engine":  result["ocr_engine"],
        "_raw_text":    result["raw_text"],
    }

def ai_explain(data: dict) -> str:
    meds = data.get("medicines", [])
    if not meds:
        return "No medicines found in the prescription."
    med_lines = "\n".join(
        f"- {m.get('name','')} {m.get('dosage','')}: {m.get('frequency','')} "
        f"for {m.get('duration','')} — {m.get('food_instruction','')}"
        for m in meds
    )
    prompt = (
        f"You are a warm eldercare assistant. Explain this prescription to an elderly patient in very simple language.\n"
        f"Patient: {data.get('patient_name', 'the patient')}\n"
        f"Medicines:\n{med_lines}\n"
        f"Diagnosis: {data.get('diagnosis', '')}\n"
        "For each medicine: what it does, how to take it, one key precaution. "
        "Keep total under 200 words. Be warm and reassuring."
    )
    return ask_gemini(prompt)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="📋 Prescription Explainer", layout="wide", page_icon="📋")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="prescription")

# ── Header ────────────────────────────────────────────────────────────────────
agent_header(
    title="📋 Prescription Explainer Agent",
    subtitle="ElderCare AI · Upload prescription image or enter details manually",
    accent="#a78bfa",
)

# ── Nav ───────────────────────────────────────────────────────────────────────
pages = ["📸 Upload Prescription", "✏️ Manual Entry", "📜 History"]
cols  = st.columns(len(pages))
if "rx_page" not in st.session_state:
    st.session_state.rx_page = pages[0]
for i, pg in enumerate(pages):
    if cols[i].button(pg, use_container_width=True,
                      type="primary" if st.session_state.rx_page == pg else "secondary"):
        st.session_state.rx_page = pg
        st.rerun()

st.divider()
page = st.session_state.rx_page

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD PRESCRIPTION IMAGE
# ══════════════════════════════════════════════════════════════════════════════
if page == "📸 Upload Prescription":
    st.subheader("📸 Upload Prescription Image")
    st.caption("Supports printed and handwritten prescriptions. Upload a clear photo for best results.")

    col_up, col_res = st.columns([1, 1])

    with col_up:
        uploaded = st.file_uploader("📷 Upload prescription photo", type=["jpg","jpeg","png","webp"])
        if uploaded:
            st.image(uploaded, caption="Uploaded Prescription", use_container_width=True)

        if uploaded and st.button("🔍 Extract & Explain Prescription", use_container_width=True, type="primary"):
            with st.spinner("🔬 Reading prescription with Gemini Vision AI..."):
                uploaded.seek(0)
                img_bytes = uploaded.read()
                data = extract_prescription_from_image(img_bytes)

            if "error" in data:
                st.error(f"❌ {data['error']}")
                api_key_set = os.getenv("GEMINI_API_KEY", "").strip()
                if not api_key_set or api_key_set == "your_gemini_api_key_here":
                    st.warning(
                        "⚠️ **Gemini API Key not set!**\n\n"
                        "To read ANY prescription (handwritten or printed):\n"
                        "1. Get a free key at https://aistudio.google.com/app/apikey\n"
                        "2. Open the `.env` file in the project root\n"
                        "3. Set: `GEMINI_API_KEY=your_actual_key_here`\n"
                        "4. Restart the agent"
                    )
                else:
                    st.info("💡 Tip: Upload a clearer, well-lit image of the prescription.")
            else:
                st.session_state.rx_extracted = data
                st.session_state.rx_explanation = ai_explain(data)
                history = _load_history()
                history.insert(0, {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "source": "image",
                    "data": data,
                    "explanation": st.session_state.rx_explanation,
                })
                _save_history(history[:50])
                prescription_to_reminder(data.get("patient_name", ""), data.get("medicines", []))
                st.rerun()

    with col_res:
        if "rx_extracted" in st.session_state:
            data = st.session_state.rx_extracted
            st.markdown("#### 📄 Extracted Prescription")

            # Confidence badge
            conf  = data.get("_confidence", 0)
            eng   = data.get("_ocr_engine", "")
            color = "#16a34a" if conf >= 0.6 else "#d97706" if conf >= 0.4 else "#dc2626"
            label = "High" if conf >= 0.6 else "Medium" if conf >= 0.4 else "Low"
            st.markdown(
                f'<div style="margin-bottom:0.5rem">' 
                f'<span style="background:{color};color:white;padding:3px 10px;'
                f'border-radius:12px;font-size:0.82rem;font-weight:600">'
                f'🎯 Confidence: {label} ({conf:.0%})</span>&nbsp;'
                f'<span style="font-size:0.8rem;color:#64748b">Engine: {eng}</span></div>',
                unsafe_allow_html=True,
            )

            st.markdown(f"""
<div class="rx-card">
<b>👤 Patient:</b> {data.get('patient_name','—')} &nbsp;|&nbsp;
<b>🩺 Doctor:</b> {data.get('doctor_name','—')} &nbsp;|&nbsp;
<b>📅 Date:</b> {data.get('date','—')}<br>
<b>🏥 Hospital:</b> {data.get('hospital','—')} &nbsp;|&nbsp;
<b>🏥 Diagnosis:</b> {data.get('diagnosis','—')}
</div>
""", unsafe_allow_html=True)

            meds = data.get("medicines", [])
            if meds:
                st.markdown("**💊 Medicines:**")
                for m in meds:
                    st.markdown(f"""
<div class="med-row">
<b>{m.get('name','')}</b> — {m.get('dosage','')}<br>
⏰ {m.get('frequency','')} &nbsp;|&nbsp; 📅 {m.get('duration','')} &nbsp;|&nbsp; 🍽️ {m.get('food_instruction','')}<br>
{('<i>'+m.get('notes','')+'</i>') if m.get('notes') else ''}
</div>
""", unsafe_allow_html=True)
            else:
                st.warning("No medicines detected. Try a clearer image.")

            if "rx_explanation" in st.session_state:
                st.markdown("#### 🤖 AI Explanation")
                st.info(st.session_state.rx_explanation)

            # Download
            meds_text = "\n\n".join(
                f"Medicine: {m.get('name','')}\nDosage: {m.get('dosage','')}\n"
                f"Frequency: {m.get('frequency','')}\nDuration: {m.get('duration','')}\n"
                f"Instruction: {m.get('food_instruction','')}"
                for m in meds
            )
            summary = (
                f"ElderCare AI — Prescription Summary\n{'='*40}\n"
                f"Patient: {data.get('patient_name','')}\n"
                f"Doctor: {data.get('doctor_name','')}\n"
                f"Date: {data.get('date','')}\n"
                f"Diagnosis: {data.get('diagnosis','')}\n\n"
                f"{meds_text}\n\n"
                f"AI Explanation:\n{st.session_state.get('rx_explanation','')}\n\n"
                "Generated by ElderCare AI"
            )
            st.download_button(
                "⬇️ Download Summary",
                data=summary.encode("utf-8"),
                file_name=f"prescription_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

            if st.button("🔄 Clear & Upload New", use_container_width=True):
                for k in ["rx_extracted", "rx_explanation"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            st.info("📌 Upload a prescription image on the left to see extracted details here.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MANUAL ENTRY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Manual Entry":
    st.subheader("✏️ Enter Prescription Details Manually")

    with st.form("manual_rx_form"):
        c1, c2 = st.columns(2)
        patient_name = c1.text_input("👤 Patient Name", placeholder="e.g. Rajan Kumar")
        doctor_name  = c2.text_input("🩺 Doctor Name",  placeholder="e.g. Dr. Priya")
        c3, c4 = st.columns(2)
        diagnosis    = c3.text_input("🏥 Diagnosis / Condition", placeholder="e.g. Type 2 Diabetes")
        rx_date      = c4.date_input("📅 Prescription Date", value=datetime.now().date())

        st.markdown("**💊 Medicine Details**")
        num_meds = st.number_input("Number of medicines", min_value=1, max_value=10, value=1, step=1)
        medicines = []
        for i in range(int(num_meds)):
            st.markdown(f"*Medicine {i+1}*")
            mc1, mc2, mc3 = st.columns(3)
            mname  = mc1.text_input("Name",    key=f"mn{i}", placeholder="e.g. Metformin")
            mdose  = mc2.text_input("Dosage",  key=f"md{i}", placeholder="e.g. 500mg")
            mfreq  = mc3.selectbox("Frequency", ["Once daily","Twice daily","Three times daily","At night","As needed"], key=f"mf{i}")
            mc4, mc5 = st.columns(2)
            mdur   = mc4.text_input("Duration", key=f"mdu{i}", placeholder="e.g. 30 days")
            mfood  = mc5.selectbox("Food Instruction", ["After food","Before food","With food","Any time"], key=f"mfi{i}")
            medicines.append({"name": mname, "dosage": mdose, "frequency": mfreq,
                               "duration": mdur, "food_instruction": mfood, "notes": ""})

        submitted = st.form_submit_button("💡 Explain Prescription", use_container_width=True, type="primary")

    if submitted:
        if not patient_name.strip():
            st.warning("Please enter patient name.")
        elif not any(m["name"].strip() for m in medicines):
            st.warning("Please enter at least one medicine name.")
        else:
            data = {
                "patient_name": patient_name, "doctor_name": doctor_name,
                "date": str(rx_date), "diagnosis": diagnosis,
                "medicines": [m for m in medicines if m["name"].strip()],
            }
            with st.spinner("🤖 Generating explanation..."):
                explanation = ai_explain(data)

            history = _load_history()
            history.insert(0, {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "source": "manual",
                "data": data,
                "explanation": explanation,
            })
            _save_history(history[:50])
            prescription_to_reminder(patient_name, [m for m in medicines if m["name"].strip()])

            st.markdown("#### 📄 Prescription Summary")
            st.markdown(f"""
<div class="rx-card">
<b>👤 Patient:</b> {patient_name} &nbsp;|&nbsp;
<b>🩺 Doctor:</b> {doctor_name} &nbsp;|&nbsp;
<b>📅 Date:</b> {rx_date}<br>
<b>🏥 Diagnosis:</b> {diagnosis}
</div>
""", unsafe_allow_html=True)

            for m in data["medicines"]:
                st.markdown(f"""
<div class="med-row">
<b>{m['name']}</b> — {m['dosage']}<br>
⏰ {m['frequency']} &nbsp;|&nbsp; 📅 {m['duration']} &nbsp;|&nbsp; 🍽️ {m['food_instruction']}
</div>
""", unsafe_allow_html=True)

            st.markdown("#### 🤖 AI Explanation")
            st.info(explanation)

            summary = build_summary_text(
                patient_name=patient_name,
                medicine_name=", ".join(m["name"] for m in data["medicines"]),
                dosage=", ".join(m["dosage"] for m in data["medicines"]),
                frequency=", ".join(m["frequency"] for m in data["medicines"]),
                duration=", ".join(m["duration"] for m in data["medicines"]),
                purpose=diagnosis,
            ) + f"\n\nAI Explanation:\n{explanation}\n\nGenerated by ElderCare AI"

            st.download_button(
                "⬇️ Download Summary",
                data=summary.encode("utf-8"),
                file_name=f"{patient_name.replace(' ','_').lower()}_prescription.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📜 History":
    st.subheader("📜 Prescription History")
    history = _load_history()

    if not history:
        st.info("No prescription history yet. Upload or enter a prescription to get started.")
    else:
        col_list, col_detail = st.columns([1, 2])

        with col_list:
            st.markdown(f"**{len(history)} record(s)**")
            if "rx_hist_idx" not in st.session_state:
                st.session_state.rx_hist_idx = 0
            for i, rec in enumerate(history):
                data = rec.get("data", {})
                label = f"{'📸' if rec.get('source')=='image' else '✏️'} {data.get('patient_name','Unknown')} — {rec['timestamp']}"
                if st.button(label, key=f"hist_{i}", use_container_width=True):
                    st.session_state.rx_hist_idx = i
                    st.rerun()

            if st.button("🗑️ Clear All History", use_container_width=True):
                _save_history([])
                st.session_state.pop("rx_hist_idx", None)
                st.rerun()

        with col_detail:
            idx  = st.session_state.get("rx_hist_idx", 0)
            rec  = history[idx] if idx < len(history) else history[0]
            data = rec.get("data", {})

            st.markdown(f"#### 📄 {data.get('patient_name','—')} — {rec['timestamp']}")
            st.markdown(f"""
<div class="rx-card">
<b>🩺 Doctor:</b> {data.get('doctor_name','—')} &nbsp;|&nbsp;
<b>📅 Date:</b> {data.get('date','—')}<br>
<b>🏥 Diagnosis:</b> {data.get('diagnosis','—')}
</div>
""", unsafe_allow_html=True)

            for m in data.get("medicines", []):
                st.markdown(f"""
<div class="med-row">
<b>{m.get('name','')}</b> — {m.get('dosage','')}<br>
⏰ {m.get('frequency','')} &nbsp;|&nbsp; 📅 {m.get('duration','')} &nbsp;|&nbsp; 🍽️ {m.get('food_instruction','')}
</div>
""", unsafe_allow_html=True)

            if rec.get("explanation"):
                st.markdown("**🤖 AI Explanation:**")
                st.info(rec["explanation"])
