"""💊 Medicine Reminder AI Agent — ElderCare AgentVerse"""
import streamlit as st
from datetime import datetime
from medicine_db import (
    get_medicine, get_generic, log_dose, get_adherence,
    get_todays_log, check_missed_count
)
from agents.medicine_reminder import chat, verify_medicine_image, analyze_missed_dose, get_voice_reminder_text

st.set_page_config(page_title="💊 Medicine Reminder AI", layout="wide", page_icon="💊")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f0f4f8; }
.header-box {
    background: linear-gradient(135deg, #1a3c5e, #2d6a9f);
    color: white; padding: 1.2rem 1.8rem; border-radius: 12px; margin-bottom: 1rem;
}
.header-box h1 { margin: 0; font-size: 1.6rem; }
.header-box p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem; }
.metric-card {
    background: white; border-radius: 10px; padding: 1rem;
    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.voice-box {
    background: #e8f4fd; border-left: 4px solid #2d6a9f;
    padding: 1rem; border-radius: 8px; font-size: 1.05rem;
}
.alert-box {
    background: #fff3cd; border-left: 4px solid #ffc107;
    padding: 0.8rem; border-radius: 8px;
}
.emergency-box {
    background: #fde8e8; border-left: 4px solid #e53e3e;
    padding: 0.8rem; border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <h1>💊 Medicine Reminder AI Agent</h1>
    <p>ElderCare AI · Smart Medicine Management · AgentVerse Hackathon</p>
</div>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
def _init():
    defaults = {
        "chat_history": [],
        "patient": "Rajan",
        "medicines": [
            {"name": "Metformin",   "dosage": "500mg", "time": "8:00 AM",  "food": "after food"},
            {"name": "Amlodipine",  "dosage": "5mg",   "time": "9:00 AM",  "food": "any time"},
            {"name": "Vitamin D",   "dosage": "1 tab", "time": "1:00 PM",  "food": "after lunch"},
            {"name": "Omeprazole",  "dosage": "20mg",  "time": "7:30 AM",  "food": "before food"},
        ],
        "reminder_sent": {},
        "caregiver_alerts": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

tab1, tab2, tab3 = st.tabs(["🤖 AI Chat & Reminders", "📊 Dashboard", "📸 Verify Medicine"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — AI Chat + Smart Reminders + Voice + Food + Emergency
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🤖 AI Medicine Assistant")

        # ── Today's reminders ─────────────────────────────────────────────
        st.markdown("#### 🔔 Today's Medicine Schedule")
        today_log = get_todays_log(st.session_state.patient)
        taken_today = {l["medicine"].lower() for l in today_log if l["status"] == "taken"}

        for med in st.session_state.medicines:
            mname = med["name"]
            mkey  = mname.lower()
            col_a, col_b, col_c = st.columns([3, 1, 1])
            status_icon = "✅" if mkey in taken_today else "⏰"
            col_a.markdown(f"{status_icon} **{mname}** — {med['dosage']} at {med['time']} _{med['food']}_")

            if mkey not in taken_today:
                if col_b.button("✅ Taken", key=f"taken_{mkey}"):
                    log_dose(st.session_state.patient, mname, "taken")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"✅ Great job, {st.session_state.patient}! I've recorded that you took **{mname}**. Keep it up! 💪"
                    })
                    st.rerun()
                if col_c.button("❌ Missed", key=f"missed_{mkey}"):
                    missed_n = check_missed_count(st.session_state.patient, mname) + 1
                    log_dose(st.session_state.patient, mname, "missed")
                    analysis = analyze_missed_dose(st.session_state.patient, mname, missed_n, "not specified")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"⚠️ Missed dose recorded for **{mname}**.\n\n{analysis}"
                    })
                    if missed_n >= 2:
                        alert = f"🔔 Caregiver Alert: {st.session_state.patient} has missed **{mname}** {missed_n} times. Please check on them."
                        st.session_state.caregiver_alerts.append(alert)
                        st.session_state.chat_history.append({"role": "assistant", "content": alert})
                    st.rerun()

        st.divider()

        # ── Chat interface ─────────────────────────────────────────────────
        st.markdown("#### 💬 Chat with AI")

        # Seed welcome message
        if not st.session_state.chat_history:
            adh = get_adherence(st.session_state.patient)
            welcome = (
                f"Hello {st.session_state.patient}! 👋 I'm your Medicine AI Assistant.\n\n"
                f"You have **{len(st.session_state.medicines)} medicines** scheduled today. "
                f"Your overall adherence is **{adh['percentage']}%**.\n\n"
                "You can ask me:\n"
                "- _\"What happens if I miss my BP tablet?\"_\n"
                "- _\"Can I take Metformin and Aspirin together?\"_\n"
                "- _\"I forgot whether I took my medicine\"_\n"
                "- _\"I'm feeling dizzy after missing insulin\"_"
            )
            st.session_state.chat_history.append({"role": "assistant", "content": welcome})

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="💊" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask about your medicines, missed doses, interactions...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # ── Emergency detection ────────────────────────────────────────
            emergency_keywords = ["dizzy", "dizziness", "chest pain", "unconscious", "faint",
                                   "can't breathe", "severe", "emergency", "help", "shaking", "confusion"]
            is_emergency = any(kw in user_input.lower() for kw in emergency_keywords)

            # ── Forgot medicine check ──────────────────────────────────────
            forgot_check = any(w in user_input.lower() for w in ["forgot whether", "don't remember", "not sure if i took"])
            if forgot_check:
                today_taken = [l["medicine"] for l in get_todays_log(st.session_state.patient) if l["status"] == "taken"]
                if today_taken:
                    context = f"[System: Patient has taken today: {', '.join(today_taken)}]"
                else:
                    context = "[System: Patient has NOT marked any medicine as taken today.]"
                full_msg = f"{context}\n\nPatient says: {user_input}"
            else:
                full_msg = user_input

            history_for_ai = st.session_state.chat_history[:-1]  # exclude current user msg
            reply = chat(history_for_ai, full_msg)

            if is_emergency:
                reply = f"🚨 **EMERGENCY DETECTED**\n\n{reply}\n\n---\n⚡ **Please contact your caregiver or call emergency services immediately if symptoms are severe.**"

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    with col_right:
        # ── Voice Reminder ─────────────────────────────────────────────────
        st.markdown("#### 🗣️ Voice Reminder")
        next_med = next(
            (m for m in st.session_state.medicines if m["name"].lower() not in taken_today),
            st.session_state.medicines[0]
        )
        voice_text = get_voice_reminder_text(
            st.session_state.patient, next_med["name"],
            next_med["dosage"], next_med["time"], next_med["food"]
        )
        st.markdown(f'<div class="voice-box">🔊 {voice_text}</div>', unsafe_allow_html=True)

        st.divider()

        # ── Drug Interaction Quick Check ───────────────────────────────────
        st.markdown("#### 🔄 Drug Interaction Check")
        med_a = st.text_input("Medicine A", placeholder="e.g. Metformin")
        med_b = st.text_input("Medicine B", placeholder="e.g. Aspirin")
        if st.button("⚡ Check Interaction"):
            if med_a and med_b:
                with st.spinner("Checking..."):
                    result = chat([], f"Can I take {med_a} and {med_b} together? Give a brief interaction warning.")
                st.info(result)
            else:
                st.warning("Enter both medicine names.")

        st.divider()

        # ── Caregiver Alerts ───────────────────────────────────────────────
        if st.session_state.caregiver_alerts:
            st.markdown("#### 👨‍👩‍👧 Caregiver Alerts")
            for alert in st.session_state.caregiver_alerts[-3:]:
                st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)

        # ── Patient Settings ───────────────────────────────────────────────
        st.divider()
        st.markdown("#### ⚙️ Patient")
        new_name = st.text_input("Patient Name", value=st.session_state.patient)
        if new_name != st.session_state.patient:
            st.session_state.patient = new_name
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Adherence Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"📊 Medicine Adherence Dashboard — {st.session_state.patient}")

    adh = get_adherence(st.session_state.patient)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><h2>{adh["total"]}</h2><p>Total Doses</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h2 style="color:#38a169">✅ {adh["taken"]}</h2><p>Taken</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h2 style="color:#e53e3e">❌ {adh["missed"]}</h2><p>Missed</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><h2 style="color:#2d6a9f">📈 {adh["percentage"]}%</h2><p>Adherence</p></div>', unsafe_allow_html=True)

    st.divider()

    # ── Adherence bar ──────────────────────────────────────────────────────
    pct = adh["percentage"]
    bar_color = "#38a169" if pct >= 80 else "#ffc107" if pct >= 50 else "#e53e3e"
    st.markdown(f"""
    <div style="background:#e2e8f0;border-radius:8px;height:24px;margin:0.5rem 0">
        <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;color:white;font-weight:bold">
            {pct}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    if pct >= 80:
        st.success("🌟 Excellent adherence! Keep it up!")
    elif pct >= 50:
        st.warning("⚠️ Moderate adherence. Try to be more consistent.")
    elif adh["total"] == 0:
        st.info("No doses logged yet. Use the reminders in the Chat tab.")
    else:
        st.error("🚨 Low adherence. Caregiver has been notified.")

    # ── Dose log table ─────────────────────────────────────────────────────
    if adh["logs"]:
        st.markdown("#### 📋 Dose History")
        import pandas as pd
        df = pd.DataFrame(adh["logs"])[["time", "medicine", "status", "note"]]
        df.columns = ["Time", "Medicine", "Status", "Note"]
        df["Status"] = df["Status"].map({"taken": "✅ Taken", "missed": "❌ Missed", "skipped": "⏭️ Skipped"}).fillna(df["Status"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Add demo data ──────────────────────────────────────────────────────
    st.divider()
    if st.button("🎲 Load Demo Data (for judges)"):
        from demo_data import load_demo
        load_demo(st.session_state.patient)
        st.success("Demo data loaded! Refresh the dashboard.")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Medicine Photo Verification
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📸 AI Medicine Verification")
    st.markdown("Upload a photo of your medicine. AI will identify it and check if it matches today's schedule.")

    scheduled_names = [m["name"] for m in st.session_state.medicines]
    selected_med = st.selectbox("Which medicine should this be?", scheduled_names)

    uploaded = st.file_uploader("📷 Upload medicine photo", type=["jpg", "jpeg", "png", "webp"])

    if uploaded:
        st.image(uploaded, caption="Uploaded Medicine", width=300)
        if st.button("🔍 Verify with AI"):
            with st.spinner("AI is analysing the medicine..."):
                result = verify_medicine_image(uploaded.read(), selected_med)
            st.markdown("#### 🤖 AI Verification Result")
            st.markdown(result)

            if "✅" in result:
                st.success("Medicine verified! You can proceed to take it.")
            elif "❌" in result:
                st.error("⚠️ This does NOT appear to match your scheduled medicine. Please double-check.")
            else:
                st.warning("AI could not confirm with certainty. Please verify manually.")
    else:
        st.info("📌 Upload a clear photo of the medicine label or tablet strip for best results.")
