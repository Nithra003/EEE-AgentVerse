"""💊 Medicine Reminder AI Agent — Login + Personal Profile"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date as _date
from users import (
    login, register, get_user, save_medicines, get_refill_alerts,
    get_todays_log, log_dose, get_adherence, check_missed_count, update_profile,
)
from agents.medicine_reminder import chat, verify_medicine_image, analyze_missed_dose, get_voice_reminder_text, analyze_prescription_image, explain_prescription_ai
from shared.agent_bridge import get_prescription_events, reminder_to_voice
from shared.ui_components import init_theme, sidebar_nav, agent_header
from shared.ui_theme import inject

st.set_page_config(page_title="💊 Medicine Reminder AI", layout="wide", page_icon="💊")
dark = init_theme()
inject(dark)
sidebar_nav(active_id="medicine")

# ── Session init ──────────────────────────────────────────────────────────────
for k, v in {"logged_in": False, "username": "", "page": "login",
              "chat_history": [], "caregiver_alerts": [], "edit_med_idx": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def speak(text: str):
    safe = text.replace("'", " ").replace('"', " ").replace("\n", " ")
    safe = safe.encode("ascii", "ignore").decode("ascii")
    components.html(f"""
    <script>
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance('{safe}');
    u.rate=0.85; u.pitch=1.0; u.volume=1.0;
    window.speechSynthesis.speak(u);
    </script>""", height=0)

def set_voice_timer(hhmm: str, speak_txt: str, r_type: str, r_date: str, day_check: str = "var dMatch=true;"):
    safe = speak_txt.replace("'", " ").replace('"', " ").replace("\n", " ")
    safe = safe.encode("ascii", "ignore").decode("ascii")
    components.html(f"""
    <script>
    (function(){{
        var target='{hhmm}';
        function check(){{
            var now=new Date();
            var hh=String(now.getHours()).padStart(2,'0');
            var mm=String(now.getMinutes()).padStart(2,'0');
            var dd=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');
            var tMatch=(hh+':'+mm===target);
            {day_check}
            if(tMatch && dMatch){{
                window.speechSynthesis.cancel();
                var u=new SpeechSynthesisUtterance('{safe}');
                u.rate=0.85; u.volume=1.0;
                window.speechSynthesis.speak(u);
                alert('Medicine Reminder\\n\\n{safe}');
            }}
            setTimeout(check, 30000);
        }}
        setTimeout(check, 10000);
    }})();
    </script>
    <div style="background:#d4edda;border:1px solid #c3e6cb;border-radius:8px;
                padding:0.7rem 1rem;font-size:0.85rem;color:#155724;">
        ⏰ Reminder set at <b>{hhmm}</b> | {r_type} — Keep this tab open!
    </div>""", height=48)

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">💊 Medicine Reminder AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">ElderCare AI · AgentVerse Hackathon</div>', unsafe_allow_html=True)

    tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username", key="li_u")
            p = st.text_input("Password", type="password", key="li_p")
            if st.form_submit_button("Login", use_container_width=True, type="primary"):
                ok, result = login(u.strip(), p)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username  = u.strip().lower()
                    st.session_state.page      = "home"
                    st.session_state.chat_history = []
                    st.rerun()
                else:
                    st.error(result)

    with tab_reg:
        with st.form("register_form"):
            ru   = st.text_input("Username",     key="rg_u")
            rn   = st.text_input("Full Name",    key="rg_n")
            rage = st.number_input("Age", 1, 120, 60, key="rg_a")
            rph  = st.text_input("Phone Number", key="rg_ph")
            rp   = st.text_input("Password",     type="password", key="rg_p")
            rp2  = st.text_input("Confirm Password", type="password", key="rg_p2")
            if st.form_submit_button("Register", use_container_width=True, type="primary"):
                if rp != rp2:
                    st.error("Passwords do not match.")
                elif len(ru.strip()) < 3:
                    st.error("Username must be at least 3 characters.")
                else:
                    ok, msg = register(ru.strip(), rp, rn.strip(), int(rage), rph.strip())
                    if ok:
                        st.success("✅ Registered! Please login.")
                    else:
                        st.error(msg)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# LOGGED IN — load user
# ══════════════════════════════════════════════════════════════════════════════
user     = get_user(st.session_state.username)
uname    = st.session_state.username
medicines = user.get("medicines", [])

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.markdown(f"""
    <div class="header-box">
        <div>
            <h1>💊 Medicine Reminder AI</h1>
            <p>Welcome, {user['name']} · Age {user['age']} · ElderCare AI</p>
        </div>
    </div>""", unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["logged_in","username","page","chat_history","caregiver_alerts","edit_med_idx"]:
            st.session_state[k] = False if k == "logged_in" else ("" if k in ["username","page"] else [])
        st.session_state.page = "login"
        st.rerun()

# ── Nav ───────────────────────────────────────────────────────────────────────
pages = ["🏠 Home", "💊 My Medicines", "⏰ Reminders", "📊 Dashboard", "📸 Verify", "👤 Profile"]
cols  = st.columns(len(pages))
for i, pg in enumerate(pages):
    if cols[i].button(pg, use_container_width=True):
        st.session_state.page = pg
        st.rerun()

st.divider()

page = st.session_state.page

# ── Refill / Follow-up Alerts (shown on all pages) ───────────────────────────
refill_alerts = get_refill_alerts(uname)
for ra in refill_alerts:
    if ra["type"] == "refill":
        st.warning(f"💊 Refill needed: **{ra['medicine']}** — only ~{ra['days_left']} day(s) of supply left. Buy more soon!")
    elif ra["type"] == "end_soon":
        st.info(f"📅 **{ra['medicine']}** course ends in {ra['days']} day(s). Consult your doctor if needed.")
    elif ra["type"] == "follow_up":
        st.warning(f"🏥 Doctor follow-up for **{ra['medicine']}** on {ra['date']} — {ra['days']} day(s) away!")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME — AI Chat + Today's Schedule
# ══════════════════════════════════════════════════════════════════════════════
if page in ["home", "🏠 Home"]:
    # ── Incoming events from Prescription Agent ───────────────────────────────
    rx_events = get_prescription_events()
    if rx_events:
        st.info(f"📋 {len(rx_events)} new prescription(s) received from Prescription Explainer Agent.")
        for ev in rx_events:
            p = ev["payload"]
            meds = p.get("medicines", [])
            if meds:
                for m in meds:
                    if m.get("name") and m["name"].strip():
                        medicines.append({
                            "name": m["name"].strip().title(),
                            "dosage": m.get("dosage", ""),
                            "time": m.get("frequency", "As prescribed"),
                            "food": m.get("food_instruction", "as prescribed"),
                            "frequency": "Daily", "days": [],
                            "start_date": "", "end_date": "",
                            "quantity": 30, "follow_up_date": "",
                        })
                save_medicines(uname, medicines)
                st.success(f"✅ Medicines from prescription auto-added for {p.get('patient_name', 'patient')}.")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🤖 AI Medicine Assistant")

        # Today's schedule
        today_log   = get_todays_log(uname)
        taken_today = {l["medicine"].lower() for l in today_log if l["status"] == "taken"}

        if medicines:
            st.markdown("#### 🔔 Today's Schedule")
            # Compute next_med before the loop so it's always available
            next_med = next((m for m in medicines if m["name"].lower() not in taken_today), medicines[0])
            for med in medicines:
                mname = med["name"]
                mkey  = mname.lower()
                icon  = "✅" if mkey in taken_today else "⏰"
                ca, cb, cc = st.columns([3, 1, 1])
                ca.markdown(f"{icon} **{mname}** — {med['dosage']} · {med['time']} · _{med['food']}_")
                if mkey not in taken_today:
                    if cb.button("✅ Taken", key=f"t_{mkey}"):
                        log_dose(uname, mname, "taken")
                        reminder_to_voice(user["name"], mname, med.get("time", ""))
                        st.session_state.chat_history.append({"role":"assistant",
                            "content": f"✅ Great job, {user['name']}! Recorded **{mname}** as taken. 💪"})
                        speak(f"Great job {user['name']}! You have taken {mname}. Well done!")
                        st.rerun()
                    if cc.button("❌ Missed", key=f"m_{mkey}"):
                        missed_n = check_missed_count(uname, mname) + 1
                        log_dose(uname, mname, "missed")
                        analysis = analyze_missed_dose(user["name"], mname, missed_n, "not specified")
                        st.session_state.chat_history.append({"role":"assistant",
                            "content": f"⚠️ Missed **{mname}**.\n\n{analysis}"})
                        if missed_n >= 2:
                            alert = f"🔔 {user['name']} missed **{mname}** {missed_n} times!"
                            st.session_state.caregiver_alerts.append(alert)
                        st.rerun()
        else:
            st.info("No medicines added yet. Go to **💊 My Medicines** to add.")

        st.divider()

        # AI Chat
        st.markdown("#### 💬 Chat with AI")
        if not st.session_state.chat_history:
            adh = get_adherence(uname)
            st.session_state.chat_history.append({"role":"assistant", "content":(
                f"Hello {user['name']}! 👋 I'm your Medicine AI Assistant.\n\n"
                f"You have **{len(medicines)} medicines** scheduled. "
                f"Adherence: **{adh['percentage']}%**\n\n"
                "Ask me anything:\n"
                "- _\"What happens if I miss my BP tablet?\"_\n"
                "- _\"Can I take Metformin and Aspirin together?\"_\n"
                "- _\"I forgot whether I took my medicine\"_\n"
                "- _\"I'm feeling dizzy\"_"
            )})

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="💊" if msg["role"]=="assistant" else "👤"):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask about your medicines...")
        if user_input:
            st.session_state.chat_history.append({"role":"user","content":user_input})
            emergency_kw = ["dizzy","chest pain","unconscious","faint","can't breathe","severe","shaking","bleeding","fell","fall"]
            is_emergency = any(k in user_input.lower() for k in emergency_kw)
            forgot_kw    = ["forgot whether","don't remember","not sure if i took","did i take"]
            if any(w in user_input.lower() for w in forgot_kw):
                taken_list = [l["medicine"] for l in get_todays_log(uname) if l["status"]=="taken"]
                ctx = f"[Today taken: {', '.join(taken_list) if taken_list else 'NONE'}]"
                full_msg = f"{ctx}\nPatient: {user_input}"
            else:
                full_msg = user_input
            reply = chat(st.session_state.chat_history[:-1], full_msg)
            if is_emergency:
                reply = f"🚨 **EMERGENCY DETECTED**\n\n{reply}\n\n---\n⚡ **Call emergency services immediately!**"
                speak("Emergency detected! Please call emergency services immediately!")
            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.rerun()

    with col_right:
        # Voice reminder
        st.markdown("#### 🗣️ Voice Reminder")
        if medicines:
            next_med  = next((m for m in medicines if m["name"].lower() not in taken_today), medicines[0])
            voice_txt = get_voice_reminder_text(user["name"], next_med["name"], next_med["dosage"], next_med["time"], next_med["food"])
            st.markdown(f'<div class="voice-box">🔊 {voice_txt}</div>', unsafe_allow_html=True)
            if st.button("🔊 Speak Now", use_container_width=True):
                speak(voice_txt)
        else:
            st.info("Add medicines to get voice reminders.")

        st.divider()

        # Caregiver alerts
        if st.session_state.caregiver_alerts:
            st.markdown("#### 👨‍👩‍👧 Caregiver Alerts")
            for alert in st.session_state.caregiver_alerts[-3:]:
                st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MY MEDICINES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💊 My Medicines":
    st.subheader("💊 My Medicines")

    # Show existing
    if medicines:
        st.markdown("#### Current Medicines")
        for i, med in enumerate(medicines):
            ca, cb, cc = st.columns([4, 1, 1])
            ca.markdown(f"**{med['name']}** — {med['dosage']} · {med['time']} · _{med['food']}_")
            if cb.button("✏️ Edit", key=f"ed_{i}"):
                st.session_state.edit_med_idx = i
                st.rerun()
            if cc.button("🗑️ Delete", key=f"del_{i}"):
                medicines.pop(i)
                save_medicines(uname, medicines)
                st.rerun()

    st.divider()

    # Edit existing medicine
    if st.session_state.edit_med_idx is not None:
        idx = st.session_state.edit_med_idx
        med = medicines[idx]
        st.markdown(f"#### ✏️ Edit — {med['name']}")
        food_opts = ["after food","before food","with food","any time","after lunch","before sleep"]
        freq_opts = ["Daily","Weekly","Specific Days"]
        day_opts  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        with st.form("edit_med_form"):
            c1, c2 = st.columns(2)
            en = c1.text_input("Medicine Name", value=med["name"])
            ed = c2.text_input("Dosage",        value=med["dosage"])
            c3, c4 = st.columns(2)
            et = c3.text_input("Time",          value=med["time"])
            ef = c4.selectbox("Food Instruction", food_opts,
                              index=food_opts.index(med["food"]) if med["food"] in food_opts else 0)
            c5, c6 = st.columns(2)
            efreq = c5.selectbox("Frequency", freq_opts,
                                 index=freq_opts.index(med.get("frequency","Daily")) if med.get("frequency","Daily") in freq_opts else 0)
            edays = c6.multiselect("Days (if Specific)", day_opts, default=med.get("days",[]))
            c7, c8 = st.columns(2)
            from datetime import date as _date
            def _parse_date(s, fallback):
                try: return _date.fromisoformat(s)
                except: return fallback
            estart  = c7.date_input("Start Date",          value=_parse_date(med.get("start_date",""), datetime.now().date()))
            eend    = c8.date_input("End Date",            value=_parse_date(med.get("end_date",""),   datetime.now().date()))
            c9, c10 = st.columns(2)
            eqty    = c9.number_input("Quantity", min_value=0, value=int(med.get("quantity",30)), step=1)
            efollow = c10.date_input("Doctor Follow-up",   value=_parse_date(med.get("follow_up_date",""), datetime.now().date()))
            c1b, c2b = st.columns(2)
            save   = c1b.form_submit_button("💾 Save",   use_container_width=True)
            cancel = c2b.form_submit_button("❌ Cancel", use_container_width=True)
        if save:
            medicines[idx] = {
                "name": en.strip(), "dosage": ed.strip(), "time": et.strip(), "food": ef,
                "frequency": efreq, "days": edays,
                "start_date": str(estart), "end_date": str(eend),
                "quantity": int(eqty), "follow_up_date": str(efollow),
            }
            save_medicines(uname, medicines)
            st.session_state.edit_med_idx = None
            st.success("✅ Medicine updated!")
            st.rerun()
        if cancel:
            st.session_state.edit_med_idx = None
            st.rerun()

    # Add new medicine
    st.markdown("#### ➕ Add New Medicine")
    with st.form("add_med_form"):
        c1, c2 = st.columns(2)
        mn  = c1.text_input("Medicine Name",   placeholder="e.g. Metformin")
        md  = c2.text_input("Dosage",          placeholder="e.g. 500mg, 1 tablet")
        c3, c4 = st.columns(2)
        mt  = c3.text_input("Time",            placeholder="e.g. 8:00 AM")
        mf  = c4.selectbox("Food Instruction", ["after food","before food","with food","any time","after lunch","before sleep"])
        c5, c6 = st.columns(2)
        mfreq = c5.selectbox("Frequency", ["Daily","Weekly","Specific Days"])
        mdays = c6.multiselect("Days (if Specific)", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
        c7, c8 = st.columns(2)
        mstart = c7.date_input("Start Date", value=datetime.now().date())
        mend   = c8.date_input("End Date",   value=datetime.now().date())
        c9, c10 = st.columns(2)
        mqty    = c9.number_input("Quantity (tablets/capsules)", min_value=0, value=30, step=1)
        mfollow = c10.date_input("Doctor Follow-up Date", value=datetime.now().date())
        if st.form_submit_button("➕ Add Medicine", use_container_width=True):
            if mn.strip():
                medicines.append({
                    "name": mn.strip().title(), "dosage": md.strip(),
                    "time": mt.strip(), "food": mf,
                    "frequency": mfreq, "days": mdays,
                    "start_date": str(mstart), "end_date": str(mend),
                    "quantity": int(mqty), "follow_up_date": str(mfollow),
                })
                save_medicines(uname, medicines)
                st.success(f"✅ {mn.title()} added!")
                st.rerun()
            else:
                st.warning("Enter medicine name.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REMINDERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⏰ Reminders":
    st.subheader("⏰ Voice Reminders")

    if "active_reminders" not in st.session_state:
        st.session_state.active_reminders = []
    if "edit_rem_idx" not in st.session_state:
        st.session_state.edit_rem_idx = None

    if not medicines:
        st.info("Add medicines first in My Medicines tab.")
    else:
        # Show active reminders
        if st.session_state.active_reminders:
            st.markdown("#### Active Reminders")
            for i, rem in enumerate(st.session_state.active_reminders):
                ca, cb, cc = st.columns([4, 1, 1])
                ca.markdown(f"**{rem['medicine']}** - {rem['time']} - {rem['freq']} - {rem['rtype']}")
                if cb.button("Edit", key=f"redit_{i}"):
                    st.session_state.edit_rem_idx = i
                    st.rerun()
                if cc.button("Delete", key=f"rdel_{i}"):
                    st.session_state.active_reminders.pop(i)
                    st.rerun()
            st.divider()

        edit_idx = st.session_state.edit_rem_idx
        edit_rem = st.session_state.active_reminders[edit_idx] if edit_idx is not None else None
        st.markdown("#### " + ("Edit Reminder" if edit_rem else "New Reminder"))

        med_names   = [m["name"] for m in medicines]
        freq_opts   = ["Once", "Twice", "Three times"]
        type_opts   = ["Daily", "Weekly", "Specific Days", "Specific Date"]
        day_opts    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

        def_med  = edit_rem["medicine"] if edit_rem and edit_rem["medicine"] in med_names else med_names[0]
        def_freq = edit_rem["freq"]     if edit_rem and edit_rem["freq"] in freq_opts    else "Once"
        def_type = edit_rem["rtype"]    if edit_rem and edit_rem["rtype"] in type_opts   else "Daily"
        def_time = datetime.now().replace(second=0, microsecond=0)
        if edit_rem:
            try:
                hh, mm = map(int, edit_rem["time"].split(":"))
                def_time = def_time.replace(hour=hh, minute=mm)
            except Exception:
                pass

        with st.form("reminder_form"):
            r_med  = st.selectbox("Medicine",      med_names,  index=med_names.index(def_med))
            r_time = st.time_input("Remind at",    value=def_time)
            r_freq = st.selectbox("Times per day", freq_opts,  index=freq_opts.index(def_freq))
            r_type = st.radio("Schedule Type",     type_opts,  index=type_opts.index(def_type), horizontal=True)
            r_days = st.multiselect("Select Days", day_opts,
                                    default=edit_rem.get("days",[]) if edit_rem else []) if r_type == "Specific Days" else []
            r_date = st.date_input("Date", value=datetime.now().date()) if r_type == "Specific Date" else None
            c1, c2 = st.columns(2)
            submit = c1.form_submit_button("Save Reminder",  use_container_width=True)
            cancel = c2.form_submit_button("Cancel",         use_container_width=True)

        if cancel:
            st.session_state.edit_rem_idx = None
            st.rerun()

        if submit:
            med_info  = next((m for m in medicines if m["name"] == r_med), {})
            food_inst = med_info.get("food", "as prescribed")
            dosage    = med_info.get("dosage", "")
            speak_txt = f"Hello {user['name']}! Time to take {r_med} {dosage} {food_inst}. Please take your medicine now!"
            speak_txt = speak_txt.encode("ascii", "ignore").decode("ascii")
            hhmm      = r_time.strftime("%H:%M")
            date_str  = r_date.strftime("%Y-%m-%d") if r_date else ""

            rem_entry = {"medicine": r_med, "time": hhmm, "freq": r_freq,
                         "rtype": r_type, "date": date_str, "days": r_days}
            if edit_idx is not None:
                st.session_state.active_reminders[edit_idx] = rem_entry
                st.session_state.edit_rem_idx = None
            else:
                st.session_state.active_reminders.append(rem_entry)

            # Build JS day-of-week check for Weekly/Specific Days
            day_map = {"Monday":1,"Tuesday":2,"Wednesday":3,"Thursday":4,"Friday":5,"Saturday":6,"Sunday":0}
            if r_type == "Specific Days" and r_days:
                js_days = str([day_map[d] for d in r_days])
                day_check = f"var allowed={js_days}; var dMatch=allowed.indexOf(now.getDay())!==-1;"
            elif r_type == "Weekly":
                # Use the first selected day or today
                js_days = str([day_map[r_days[0]]] if r_days else [datetime.now().weekday()])
                day_check = f"var allowed={js_days}; var dMatch=allowed.indexOf(now.getDay())!==-1;"
            elif r_type == "Specific Date":
                day_check = f"var dMatch=(dd==='{date_str}');"
            else:  # Daily
                day_check = "var dMatch=true;"

            offsets = {"Once": [0], "Twice": [0, 480], "Three times": [0, 300, 600]}[r_freq]
            for off in offsets:
                h = (r_time.hour * 60 + r_time.minute + off) // 60 % 24
                m = (r_time.minute + off) % 60
                set_voice_timer(f"{h:02d}:{m:02d}", speak_txt, r_type, date_str, day_check)

            label = f"{r_type}" + (f" ({', '.join(r_days)})" if r_days else "")
            st.success(f"Reminder saved for {r_med} at {hhmm} — {r_freq} — {label}")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.subheader(f"📊 Adherence Dashboard — {user['name']}")
    adh = get_adherence(uname)
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><h2>{adh["total"]}</h2><p>Total</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h2 style="color:#38a169">✅ {adh["taken"]}</h2><p>Taken</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h2 style="color:#e53e3e">❌ {adh["missed"]}</h2><p>Missed</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><h2 style="color:#2d6a9f">📈 {adh["percentage"]}%</h2><p>Adherence</p></div>', unsafe_allow_html=True)

    pct = adh["percentage"]
    bar = "#38a169" if pct>=80 else "#ffc107" if pct>=50 else "#e53e3e"
    st.markdown(f"""
    <div style="background:#e2e8f0;border-radius:8px;height:28px;margin:1rem 0">
        <div style="background:{bar};width:{max(pct,3)}%;height:100%;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;color:white;font-weight:600">
            {pct}%
        </div>
    </div>""", unsafe_allow_html=True)

    if pct>=80:        st.success("🌟 Excellent adherence!")
    elif pct>=50:      st.warning("⚠️ Moderate. Try to be consistent.")
    elif adh["total"]==0: st.info("No doses logged yet.")
    else:              st.error("🚨 Low adherence!")

    if adh["logs"]:
        import pandas as pd
        df = pd.DataFrame(adh["logs"])[["time","medicine","status"]]
        df.columns = ["Time","Medicine","Status"]
        df["Status"] = df["Status"].map({"taken":"✅ Taken","missed":"❌ Missed"}).fillna(df["Status"])
        st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VERIFY MEDICINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📸 Verify":
    st.subheader("📸 AI Medicine Verification")
    opts     = ["Any / Just Identify"] + [m["name"] for m in medicines]
    sel_med  = st.selectbox("Expected medicine", opts)
    uploaded = st.file_uploader("📷 Upload photo", type=["jpg","jpeg","png","webp"])
    if uploaded:
        img_bytes = uploaded.read()
        st.image(img_bytes, width=300)
        if st.button("🔍 Verify with AI"):
            check = "any medicine, just identify it" if sel_med=="Any / Just Identify" else sel_med
            with st.spinner("AI reading label..."):
                result = verify_medicine_image(img_bytes, check)
            st.markdown("#### 🤖 Result")
            st.markdown(result)
            if "✅" in result:
                st.success("✅ Verified!")
                speak(f"Medicine verified. This is {sel_med}.")
            elif "❌" in result:
                st.error("❌ Does not match!")
                speak("Warning! Medicine does not match. Please check again.")
            else:
                st.warning("⚠️ Uncertain. Verify manually.")
    else:
        st.info("📌 Upload a clear photo of the medicine label.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile":
    st.subheader("👤 My Profile")
    with st.form("profile_form"):
        pn  = st.text_input("Full Name",    value=user["name"])
        pa  = st.number_input("Age", 1, 120, int(user["age"]))
        pph = st.text_input("Phone Number", value=user.get("phone",""))
        st.text_input("Username", value=uname, disabled=True)
        if st.form_submit_button("💾 Save Profile", use_container_width=True):
            update_profile(uname, pn.strip(), int(pa), pph.strip())
            st.success("✅ Profile updated!")
            st.rerun()
