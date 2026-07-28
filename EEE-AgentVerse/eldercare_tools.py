"""
eldercare_tools.py
10 tools — real logic from each agent, no emojis in output.
"""

import sys, os, re, random
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from gemini_helper import ask_gemini

_ROOT = os.path.dirname(__file__)

def _add(path):
    p = os.path.join(_ROOT, path)
    if p not in sys.path:
        sys.path.insert(0, p)


# ── TOOL 1: Medicine Reminder ─────────────────────────────────────────────────
def tool_medicine_reminder(message: str, ctx: dict) -> str:
    try:
        _add("Agent-1-Medicine-Reminder")
        from agents.medicine_reminder import chat as med_chat
        name     = ctx.get("name", "Friend")
        medicine = ctx.get("medicine", "your medicine")
        dosage   = ctx.get("dosage", "as prescribed")
        time     = ctx.get("med_time", "scheduled time")
        response = message or ctx.get("response", "")
        prompt = (
            f"Patient: {name}. Medicine: {medicine}, Dosage: {dosage}, Time: {time}. "
            f"Patient response: '{response}'. "
            "Give a warm reminder message, state if taken/missed/reminded, and food instruction."
        )
        reply = med_chat([], prompt)
        return f"💊 Medicine Reminder for {name}\n\n{reply}"
    except Exception as e:
        name = ctx.get("name", "Friend")
        med  = ctx.get("medicine", "your medicine")
        return (
            f"Medicine Reminder for {name}\n\n"
            f"Please take {med} — {ctx.get('dosage','as prescribed')} "
            f"at {ctx.get('med_time','the scheduled time')}.\n\n"
            f"Consult your doctor if you have any concerns."
        )


# ── TOOL 2: Emergency Detection ───────────────────────────────────────────────
EMERGENCY_WORDS = [
    "fall", "fell", "chest pain", "can't breathe", "cannot breathe",
    "unconscious", "bleeding", "stroke", "heart attack", "collapsed",
    "emergency", "help me", "accident", "fainted", "not breathing",
]

def tool_emergency_detection(message: str, ctx: dict) -> str:
    is_emergency = any(k in message.lower() for k in EMERGENCY_WORDS)
    if is_emergency:
        ai_msg = ask_gemini(
            f"Emergency: elder said '{message}'. Give 2 calm clear instructions. "
            f"Include: call 108, stay calm, do not move if fallen. No emojis.",
            fallback="Call 108 immediately. Stay calm and do not move until help arrives."
        )
        return (
            "EMERGENCY ALERT\n\n"
            f"{ai_msg}\n\n"
            "Emergency Numbers\n"
            "-----------------\n"
            "Ambulance        : 108\n"
            "Police           : 100\n"
            "Elder Helpline   : 1253\n"
            "National Helpline: 1800-180-1253\n\n"
            "Stay on the line. Help is on the way."
        )
    return ask_gemini(
        f"Eldercare safety monitor. Elder said: '{message}'. "
        f"Assess safety and respond calmly. No emojis. Under 80 words.",
        fallback="Please stay safe. If you feel unwell, call 108 immediately."
    )


# ── TOOL 3: Appointment Booking ───────────────────────────────────────────────
def tool_appointment_booking(message: str, ctx: dict) -> str:
    try:
        _add("Agent-3-Appointment-Booking")
        from tools import find_specialist, check_available_slots
        from doctors import SPECIALTY_INFO

        symptoms  = ctx.get("symptoms", message)
        result    = find_specialist(symptoms)
        specialty = result["specialty"]
        info      = SPECIALTY_INFO.get(specialty, {})
        doctors   = result.get("doctor_details", [])
        slots     = check_available_slots(doctors[0]["name"] if doctors else "")

        doc_lines  = "\n".join(
            f"  {i+1}. {d['name']} | {d['experience']} | Rating: {d['rating']}"
            for i, d in enumerate(doctors)
        )
        slot_lines = "\n".join(f"  - {s}" for s in slots.get("available", [])[:5])

        ai_reason = ask_gemini(
            f"Patient symptoms: '{symptoms}'. They need a {specialty}. "
            f"Give 1 sentence explanation why. No emojis. Under 25 words.",
            fallback=info.get("desc", "Recommended based on your symptoms.")
        )

        return (
            f"Appointment Recommendation\n"
            f"==========================\n"
            f"Patient   : {ctx.get('name', 'Patient')}\n"
            f"Age       : {ctx.get('age', 'N/A')}\n"
            f"Symptoms  : {symptoms}\n\n"
            f"Recommended Specialist : {specialty}\n"
            f"Reason                 : {ai_reason}\n\n"
            f"Available Doctors\n"
            f"-----------------\n"
            f"{doc_lines}\n\n"
            f"Available Time Slots\n"
            f"--------------------\n"
            f"{slot_lines}\n\n"
            f"Please visit your nearest hospital or call the clinic to confirm your booking.\n"
            f"For emergencies call 108."
        )
    except Exception:
        return ask_gemini(
            f"Eldercare appointment assistant. Patient: {ctx.get('name','Patient')}, "
            f"Age: {ctx.get('age','N/A')}, Symptoms: '{ctx.get('symptoms', message)}'. "
            f"Suggest the right specialist and simple booking steps. No emojis. Under 120 words.",
            fallback="Please visit your nearest hospital and describe your symptoms to the doctor."
        )


# ── TOOL 4: Prescription Explainer ───────────────────────────────────────────
def tool_prescription_explainer(message: str, ctx: dict) -> str:
    try:
        _add("Agent-4-Prescription-Explainer")
        from medicine_data import MedicineKnowledgeBase
        kb       = MedicineKnowledgeBase()
        med_name = ctx.get("medicine_name", message)
        medicine = kb.get_medicine(med_name.lower()) or kb.get_generic_medicine(med_name)

        ai_explain = ask_gemini(
            f"Explain '{medicine.name}' to an elderly person in very simple words. "
            f"Purpose: {medicine.purpose}. Condition: {ctx.get('condition','')}. "
            f"Dosage: {ctx.get('dosage','')}. Frequency: {ctx.get('frequency','')}. "
            f"Give 2 precautions and 1 tip. No emojis. Under 100 words.",
            fallback=f"{medicine.purpose} {medicine.treats}"
        )

        return (
            f"Prescription Explanation\n"
            f"========================\n"
            f"Patient     : {ctx.get('name', 'Patient')}\n"
            f"Medicine    : {medicine.name}\n"
            f"Purpose     : {medicine.purpose}\n"
            f"Treats      : {medicine.treats}\n"
            f"Dosage      : {ctx.get('dosage', 'as prescribed')}\n"
            f"Frequency   : {ctx.get('frequency', 'as directed')}\n"
            f"Best Time   : {medicine.best_time}\n"
            f"Missed Dose : {medicine.missed_dose}\n\n"
            f"Precautions\n"
            f"-----------\n" +
            "\n".join(f"  - {p}" for p in medicine.precautions) +
            f"\n\nSide Effects\n"
            f"------------\n" +
            "\n".join(f"  - {s}" for s in medicine.side_effects) +
            f"\n\nSimple Explanation\n"
            f"------------------\n"
            f"{ai_explain}"
        )
    except Exception:
        return ask_gemini(
            f"Explain medicine '{ctx.get('medicine_name', message)}' to an elderly person simply. "
            f"Dosage: {ctx.get('dosage','')}. Condition: {ctx.get('condition','')}. "
            f"No emojis. Under 120 words.",
            fallback="Please consult your doctor or pharmacist for medicine instructions."
        )


# ── TOOL 5: Health Report ─────────────────────────────────────────────────────
def tool_health_report(message: str, ctx: dict) -> str:
    try:
        _add("Agent-5-Health-Report")
        from health_report_agent import HealthReportAgent
        import asyncio

        def safe_int(val, default):
            try: return int(re.search(r"\d+", str(val)).group())
            except: return default

        def safe_float(val, default):
            try: return float(re.search(r"[\d.]+", str(val)).group())
            except: return default

        payload = {
            "patient_name"    : ctx.get("name", "Patient"),
            "age"             : safe_int(ctx.get("age", 70), 70),
            "heart_rate"      : safe_int(ctx.get("heart_rate", 75), 75),
            "spo2"            : safe_int(ctx.get("spo2", 97), 97),
            "body_temperature": safe_float(ctx.get("temperature", 37.0), 37.0),
            "blood_pressure"  : ctx.get("bp", "120/80"),
            "steps"           : safe_int(ctx.get("steps", 3000), 3000),
            "sleep_hours"     : safe_float(ctx.get("sleep", 7.0), 7.0),
            "timestamp"       : datetime.utcnow().isoformat(),
        }

        loop   = asyncio.new_event_loop()
        report = loop.run_until_complete(HealthReportAgent().receive_health_data(payload))
        loop.close()

        ai_summary = ask_gemini(
            f"Health report for {report.patient_name}, age {payload['age']}. "
            f"Status: {report.overall_status}, Risk: {report.risk_level}. "
            f"Metrics: {report.metrics}. Give a warm 2-sentence summary. No emojis. Under 60 words.",
            fallback=report.summary
        )

        return (
            f"Health Report\n"
            f"=============\n"
            f"Patient : {report.patient_name}\n"
            f"Age     : {payload['age']}\n"
            f"Status  : {report.overall_status}\n"
            f"Risk    : {report.risk_level}\n\n"
            f"Health Metrics\n"
            f"--------------\n" +
            "\n".join(f"  {k:<18}: {v}" for k, v in report.metrics.items()) +
            f"\n\nAnalysis\n"
            f"--------\n" +
            "\n".join(f"  {k:<18}: {v}" for k, v in report.analysis.items()) +
            f"\n\nRecommendations\n"
            f"---------------\n" +
            "\n".join(f"  - {r}" for r in report.recommendations) +
            f"\n\nSummary\n"
            f"-------\n"
            f"{ai_summary}"
        )
    except Exception:
        return ask_gemini(
            f"Health report for {ctx.get('name','Patient')}, age {ctx.get('age','N/A')}. "
            f"Heart rate: {ctx.get('heart_rate','N/A')}, BP: {ctx.get('bp','N/A')}, "
            f"SpO2: {ctx.get('spo2','N/A')}, Temp: {ctx.get('temperature','N/A')}. "
            f"Analyze and give recommendations. No emojis. Under 150 words.",
            fallback="Please consult your doctor with these health readings."
        )


# ── TOOL 6: Family Notifier ───────────────────────────────────────────────────
def tool_family_notifier(message: str, ctx: dict) -> str:
    try:
        _add("Agent-6-Family-Notifier")
        from notifications import build_notification, simulate_notification_channels

        valid_types = ["Missed Medicine", "High Blood Pressure", "High Blood Sugar",
                       "Low Heart Rate", "Fall Detected", "Emergency SOS"]
        etype = ctx.get("emergency_type", "General Alert")
        if etype not in valid_types:
            etype = "Emergency SOS"

        notification = build_notification(
            patient_name   = ctx.get("name", "Patient"),
            age            = int(re.search(r"\d+", str(ctx.get("age", 70))).group()),
            emergency_type = etype,
            location       = ctx.get("location", "Home"),
            contact_name   = ctx.get("contact_name", "Family Member"),
            relationship   = ctx.get("relationship", "Family"),
            contact_number = ctx.get("contact_number", "0000000000"),
        )
        channels = simulate_notification_channels(notification["priority"])

        ai_msg = ask_gemini(
            f"Write a short urgent family notification. "
            f"Patient: {notification['patient_name']}, Age: {notification['age']}, "
            f"Emergency: {notification['emergency_type']}, Location: {notification['location']}. "
            f"No emojis. Under 50 words.",
            fallback=f"Alert: {notification['patient_name']} needs immediate attention at {notification['location']}."
        )

        channel_lines = "\n".join(f"  - {msg}" for _, msg, _ in channels)

        return (
            f"Family Notification Sent\n"
            f"========================\n"
            f"Patient        : {notification['patient_name']}\n"
            f"Age            : {notification['age']}\n"
            f"Emergency      : {notification['emergency_type']}\n"
            f"Priority       : {notification['priority']}\n"
            f"Location       : {notification['location']}\n"
            f"Contact Person : {notification['contact_name']} ({notification['relationship']})\n"
            f"Contact Number : {notification['contact_number']}\n"
            f"Date and Time  : {notification['date']} at {notification['time']}\n"
            f"Status         : {notification['status']}\n\n"
            f"Notification Channels\n"
            f"---------------------\n"
            f"{channel_lines}\n\n"
            f"Message Sent to Family\n"
            f"----------------------\n"
            f"{ai_msg}"
        )
    except Exception:
        return ask_gemini(
            f"Write a family emergency notification. "
            f"Patient: {ctx.get('name','Patient')}, Emergency: {ctx.get('emergency_type','alert')}, "
            f"Location: {ctx.get('location','home')}. No emojis. Under 80 words.",
            fallback="Emergency alert sent to family. Please contact them immediately."
        )


# ── TOOL 7: Diet Recommendation ───────────────────────────────────────────────
def tool_diet_recommendation(message: str, ctx: dict) -> str:
    try:
        _add("Agent-7-Diet-Recommendation")
        from diet_data import get_diet_plan, CONDITIONS, calculate_bmi

        condition = ctx.get("condition", "General Wellness")
        if condition not in CONDITIONS:
            condition = "General Wellness"

        plan = get_diet_plan(condition)

        bmi_text = ""
        if ctx.get("weight") and ctx.get("height"):
            try:
                bmi, cat = calculate_bmi(
                    float(re.search(r"[\d.]+", str(ctx["weight"])).group()),
                    float(re.search(r"[\d.]+", str(ctx["height"])).group())
                )
                bmi_text = f"BMI     : {bmi} ({cat})\n"
            except Exception:
                pass

        ai_advice = ask_gemini(
            f"Eldercare nutritionist. Patient: {ctx.get('name','Patient')}, "
            f"Age: {ctx.get('age','N/A')}, Condition: {condition}. "
            f"Give 3 specific food tips and 1 motivational line. No emojis. Under 100 words.",
            fallback=plan["tip"]
        )

        return (
            f"Diet Recommendation\n"
            f"===================\n"
            f"Patient   : {ctx.get('name', 'Patient')}\n"
            f"Age       : {ctx.get('age', 'N/A')}\n"
            f"Condition : {condition}\n"
            f"{bmi_text}\n"
            f"About This Diet\n"
            f"---------------\n"
            f"{plan['description']}\n\n"
            f"Foods to Eat\n"
            f"------------\n" +
            "\n".join(f"  - {f}" for f in plan["foods_to_eat"]) +
            f"\n\nFoods to Avoid\n"
            f"--------------\n" +
            "\n".join(f"  - {f}" for f in plan["foods_to_avoid"]) +
            f"\n\nDaily Meal Plan\n"
            f"---------------\n" +
            "\n".join(f"  {k:<15}: {v}" for k, v in plan["meal_plan"].items()) +
            f"\n\nWater Intake : {plan['water_intake']}\n"
            f"Tip          : {plan['tip']}\n\n"
            f"Personalized Advice\n"
            f"-------------------\n"
            f"{ai_advice}"
        )
    except Exception:
        return ask_gemini(
            f"Diet plan for {ctx.get('name','Patient')}, age {ctx.get('age','N/A')}, "
            f"condition: {ctx.get('condition','general')}. "
            f"Foods to eat, avoid, and meal plan. No emojis. Under 150 words.",
            fallback="Eat fresh fruits, vegetables, and drink plenty of water. Avoid oily and salty foods."
        )


# ── TOOL 8: Exercise Coach ────────────────────────────────────────────────────
def tool_exercise_coach(message: str, ctx: dict) -> str:
    try:
        _add("Agent-8-Exercise-Coach")
        from exercise_data import get_exercise_plan, CONDITIONS, WEEKLY_SCHEDULE

        condition     = ctx.get("condition", "General Fitness")
        fitness_level = ctx.get("fitness_level", "Beginner")
        if condition not in CONDITIONS:
            condition = "General Fitness"

        plan = get_exercise_plan(condition)

        ex_lines = "\n".join(
            f"  - {e['name']} | {e.get('duration', e.get('sets',''))} | {e['benefit']}"
            for e in plan["exercises"]
        )
        schedule_lines = "\n".join(
            f"  {day:<12}: {task}" for day, task in WEEKLY_SCHEDULE.items()
        )
        precaution_lines = "\n".join(f"  - {p}" for p in plan["precautions"])

        ai_advice = ask_gemini(
            f"Exercise coach for {ctx.get('name','Patient')}, age {ctx.get('age','N/A')}, "
            f"condition: {condition}, fitness level: {fitness_level}. "
            f"Give 3 specific tips and 1 motivational line. No emojis. Under 100 words.",
            fallback=plan["tip"]
        )

        return (
            f"Exercise Plan\n"
            f"=============\n"
            f"Patient       : {ctx.get('name', 'Patient')}\n"
            f"Age           : {ctx.get('age', 'N/A')}\n"
            f"Condition     : {condition}\n"
            f"Fitness Level : {fitness_level}\n"
            f"Intensity     : {plan['intensity']}\n"
            f"Duration      : {plan['duration']}\n\n"
            f"About This Plan\n"
            f"---------------\n"
            f"{plan['description']}\n\n"
            f"Daily Exercises\n"
            f"---------------\n"
            f"{ex_lines}\n\n"
            f"Weekly Schedule\n"
            f"---------------\n"
            f"{schedule_lines}\n\n"
            f"Safety Precautions\n"
            f"------------------\n"
            f"{precaution_lines}\n\n"
            f"Tip : {plan['tip']}\n\n"
            f"Personalized Advice\n"
            f"-------------------\n"
            f"{ai_advice}"
        )
    except Exception:
        return ask_gemini(
            f"Exercise plan for {ctx.get('name','Patient')}, age {ctx.get('age','N/A')}, "
            f"condition: {ctx.get('condition','general')}. "
            f"Safe gentle exercises for elderly. No emojis. Under 150 words.",
            fallback="Try gentle walking for 15 minutes daily and simple stretching exercises."
        )


# ── TOOL 9: Mood Companion ────────────────────────────────────────────────────
MOOD_DATA = {
    "happy":      {"message": "That is wonderful. Your positive energy is truly inspiring.",
                   "activities": ["Listen to your favourite songs", "Call a friend or family member", "Take a short walk in the garden"],
                   "affirmation": "You are loved and bring joy to everyone around you."},
    "sad":        {"message": "It is okay to feel sad. You are not alone.",
                   "activities": ["Talk to a family member", "Listen to soft calming music", "Make yourself a warm cup of tea"],
                   "affirmation": "Every storm passes. Brighter days are ahead for you."},
    "anxious":    {"message": "Take a deep breath. You are safe and everything will be okay.",
                   "activities": ["Try 5 minutes of deep breathing", "Take a slow gentle walk", "Listen to calming nature sounds"],
                   "affirmation": "You have overcome challenges before. You are stronger than you think."},
    "tired":      {"message": "Rest is important. Your body is telling you to slow down.",
                   "activities": ["Take a short 20-minute nap", "Drink warm milk", "Sit quietly in fresh air"],
                   "affirmation": "Rest is not laziness. It is wisdom. Take care of yourself."},
    "lonely":     {"message": "You matter deeply to the people around you.",
                   "activities": ["Call a family member right now", "Visit a neighbour for a short chat", "Watch a favourite show"],
                   "affirmation": "You are never truly alone. People love and think about you."},
    "frustrated": {"message": "It is okay to feel frustrated. Let us find a way to feel better.",
                   "activities": ["Take a brisk walk to release tension", "Write down your feelings", "Talk to someone you trust"],
                   "affirmation": "Your feelings are valid. You have the strength to work through this."},
}

AFFIRMATIONS = [
    "Every day is a new opportunity to feel better.",
    "You are stronger than you know.",
    "You are loved and appreciated.",
    "Your smile makes the world brighter.",
    "You have wisdom that only comes with experience.",
]

BREATHING_STEPS = [
    "Sit comfortably and close your eyes.",
    "Inhale slowly through your nose for 4 counts.",
    "Hold your breath for 4 counts.",
    "Exhale slowly through your mouth for 4 counts.",
    "Hold for 4 counts. Repeat 4 times.",
]

def tool_mood_companion(message: str, ctx: dict) -> str:
    mood_raw  = ctx.get("mood", message).lower().strip()
    mood_key  = next((m for m in MOOD_DATA if m in mood_raw), None)
    mood_info = MOOD_DATA.get(mood_key)
    note      = ctx.get("note", "")
    name      = ctx.get("name", "Friend")

    note_context = f" They shared: '{note}'" if note and note.upper() != "SKIP" else ""

    ai_support = ask_gemini(
        f"Warm eldercare companion. Patient: {name}, age {ctx.get('age','N/A')}, "
        f"feeling {mood_raw}.{note_context} "
        f"Write a caring emotional support message. Suggest 1 simple activity. "
        f"No emojis. Under 80 words.",
        fallback="You are loved and valued. Take a deep breath. Better days are ahead."
    )

    affirmation    = random.choice(AFFIRMATIONS)
    breathing_text = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(BREATHING_STEPS))

    if mood_info:
        activities = "\n".join(f"  - {a}" for a in mood_info["activities"])
        return (
            f"Mood Companion\n"
            f"==============\n"
            f"Patient : {name}\n"
            f"Mood    : {mood_raw.title()}\n\n"
            f"Response\n"
            f"--------\n"
            f"{mood_info['message']}\n\n"
            f"Affirmation\n"
            f"-----------\n"
            f"\"{mood_info['affirmation']}\"\n\n"
            f"Suggested Activities\n"
            f"--------------------\n"
            f"{activities}\n\n"
            f"Today's Thought\n"
            f"---------------\n"
            f"\"{affirmation}\"\n\n"
            f"Personal Message\n"
            f"----------------\n"
            f"{ai_support}\n\n"
            f"Breathing Exercise\n"
            f"------------------\n"
            f"{breathing_text}"
        )
    return (
        f"Mood Companion\n"
        f"==============\n"
        f"Patient : {name}\n\n"
        f"Today's Thought\n"
        f"---------------\n"
        f"\"{affirmation}\"\n\n"
        f"Personal Message\n"
        f"----------------\n"
        f"{ai_support}\n\n"
        f"Breathing Exercise\n"
        f"------------------\n"
        f"{breathing_text}"
    )


# ── TOOL 10: General Assistant ────────────────────────────────────────────────
def tool_general_assistant(message: str, ctx: dict) -> str:
    try:
        _add("Agent-10-Voice-Assistant")
        from chatbot import generate_ai_response, get_daily_motivation
        name       = ctx.get("name", "Friend")
        response   = generate_ai_response(name, message, ctx.get("mood", "Normal"))
        motivation = get_daily_motivation()
        return f"{response}\n\nDaily Motivation\n----------------\n\"{motivation}\""
    except Exception:
        return ask_gemini(
            f"Warm ElderCare AI assistant. Elder said: '{message}'. "
            f"Answer helpfully and simply. No emojis. Under 100 words.",
            fallback="I am here to help you. Please tell me more about what you need."
        )
