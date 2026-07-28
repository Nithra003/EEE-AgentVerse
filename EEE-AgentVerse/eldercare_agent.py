"""
eldercare_agent.py
Real conversational ElderCare AI Agent.
Asks questions step by step, remembers answers, then acts.
PERCEIVE -> THINK -> ACT -> RESPOND
"""

import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))

from gemini_helper import ask_gemini
from eldercare_tools import (
    tool_medicine_reminder, tool_emergency_detection,
    tool_appointment_booking, tool_prescription_explainer,
    tool_health_report, tool_family_notifier,
    tool_diet_recommendation, tool_exercise_coach,
    tool_mood_companion, tool_general_assistant,
)

# ── intent keywords for routing ───────────────────────────────────────────────
INTENT_MAP = {
    "medicine_reminder":      ["medicine", "tablet", "pill", "dose", "forgot medicine", "medication", "reminder", "drug"],
    "emergency_detection":    ["fall", "fell", "chest pain", "emergency", "accident", "help", "breathe", "bleeding", "fainted", "collapsed", "stroke", "heart attack"],
    "appointment_booking":    ["book", "appointment", "doctor", "specialist", "clinic", "hospital visit", "consult"],
    "prescription_explainer": ["prescription", "explain medicine", "what is this medicine", "side effect", "how to take"],
    "health_report":          ["blood pressure", "sugar", "heart rate", "bp", "glucose", "spo2", "vitals", "health report", "health numbers"],
    "family_notifier":        ["notify family", "alert family", "inform family", "contact family", "send message family"],
    "diet_recommendation":    ["diet", "food", "eat", "meal", "nutrition", "what to eat", "avoid food"],
    "exercise_coach":         ["exercise", "workout", "walk", "yoga", "stretching", "fitness", "physical"],
    "mood_companion":         ["sad", "lonely", "anxious", "happy", "tired", "frustrated", "feeling", "mood", "emotional", "depress", "worry"],
    "general_assistant":      [],
}

# ── conversation flows for each tool ─────────────────────────────────────────
FLOWS = {
    "medicine_reminder": [
        ("name",      "What is your name?"),
        ("medicine",  "What is the name of the medicine?"),
        ("dosage",    "What is the dosage? For example: 1 tablet, 500 mg."),
        ("med_time",  "At what time should you take this medicine?"),
        ("response",  "Have you taken your medicine? You can say yes, no, or I forgot."),
    ],
    "appointment_booking": [
        ("name",     "What is your name?"),
        ("age",      "How old are you?"),
        ("symptoms", "What symptoms are you experiencing? Please describe how you feel."),
        ("phone",    "What is your mobile number?"),
    ],
    "prescription_explainer": [
        ("name",          "What is your name?"),
        ("medicine_name", "What is the name of the medicine you want explained?"),
        ("dosage",        "What is the dosage written on the prescription?"),
        ("frequency",     "How often should it be taken? For example: twice daily, once at night."),
        ("condition",     "What condition is this medicine prescribed for?"),
    ],
    "health_report": [
        ("name",        "What is your name?"),
        ("age",         "How old are you?"),
        ("heart_rate",  "What is your heart rate in bpm? For example: 75"),
        ("spo2",        "What is your oxygen level (SpO2)? For example: 97"),
        ("bp",          "What is your blood pressure? For example: 120/80"),
        ("temperature", "What is your body temperature in Celsius? For example: 37.0"),
        ("steps",       "How many steps did you walk today? For example: 3000"),
        ("sleep",       "How many hours did you sleep last night? For example: 7"),
    ],
    "family_notifier": [
        ("name",           "What is the patient's name?"),
        ("age",            "How old is the patient?"),
        ("location",       "What is the patient's current location?"),
        ("emergency_type", "What type of emergency is this? Options: Missed Medicine, High Blood Pressure, High Blood Sugar, Low Heart Rate, Fall Detected, Emergency SOS"),
        ("contact_name",   "What is the emergency contact person's name?"),
        ("relationship",   "What is their relationship? Options: Son, Daughter, Spouse, Caregiver, Friend, Other"),
        ("contact_number", "What is their 10-digit mobile number?"),
    ],
    "diet_recommendation": [
        ("name",      "What is your name?"),
        ("age",       "How old are you?"),
        ("weight",    "What is your weight in kg? For example: 70"),
        ("height",    "What is your height in cm? For example: 165"),
        ("condition", "What is your health condition? Options: Diabetes, High Blood Pressure, Heart Disease, Arthritis, General Wellness"),
    ],
    "exercise_coach": [
        ("name",          "What is your name?"),
        ("age",           "How old are you?"),
        ("condition",     "What is your health condition? Options: General Fitness, Diabetes Management, High Blood Pressure, Arthritis, Post-Recovery"),
        ("fitness_level", "What is your fitness level? Options: Beginner, Intermediate, Active"),
    ],
    "mood_companion": [
        ("name", "What is your name?"),
        ("age",  "How old are you?"),
        ("mood", "How are you feeling right now? Options: Happy, Sad, Anxious, Tired, Lonely, Frustrated"),
        ("note", "Would you like to share anything about your day? You can also say skip."),
    ],
    "medicine_reminder_check": [
        ("name",     "What is your name?"),
        ("medicine", "Which medicine did you miss or want a reminder for?"),
    ],
}

TOOL_LABELS = {
    "medicine_reminder":      "Medicine Reminder",
    "emergency_detection":    "Emergency Detection",
    "appointment_booking":    "Appointment Booking",
    "prescription_explainer": "Prescription Explainer",
    "health_report":          "Health Report",
    "family_notifier":        "Family Notifier",
    "diet_recommendation":    "Diet Recommendation",
    "exercise_coach":         "Exercise Coach",
    "mood_companion":         "Mood Companion",
    "general_assistant":      "General Assistant",
}


class ElderCareAgent:
    """
    Real conversational ElderCare AI Agent.
    - Detects intent from first message
    - Asks questions one by one
    - Remembers all answers
    - Calls the correct tool with full context
    - Responds like a caring companion
    """

    def __init__(self):
        self.context      : dict  = {}   # all collected info
        self.history      : list  = []   # full chat history
        self.current_tool : str   = ""   # which tool is active
        self.flow         : list  = []   # current question flow
        self.flow_index   : int   = 0    # which question we are on
        self.collecting   : bool  = False # always set in __init__
        self.turn         : int   = 0

    # guard — Streamlit sometimes re-creates objects partially
    def __getattr__(self, name):
        defaults = {
            "collecting": False, "flow": [], "flow_index": 0,
            "current_tool": "", "context": {}, "history": [], "turn": 0,
        }
        if name in defaults:
            setattr(self, name, defaults[name])
            return defaults[name]
        raise AttributeError(f"ElderCareAgent has no attribute '{name}'")

    # ── PERCEIVE ──────────────────────────────────────────────────────────────
    def perceive(self, message: str) -> str:
        msg = message.strip()
        self.history.append({"role": "user", "content": msg})
        return msg

    # ── THINK — detect intent ─────────────────────────────────────────────────
    def detect_intent(self, message: str) -> str:
        msg_lower = message.lower()

        # emergency always first — no questions needed
        emergency_words = ["fall", "fell", "chest pain", "emergency", "help me",
                           "can't breathe", "bleeding", "fainted", "collapsed",
                           "stroke", "heart attack", "not breathing", "unconscious"]
        if any(w in msg_lower for w in emergency_words):
            return "emergency_detection"

        # keyword scoring
        scores = {}
        for tool, keywords in INTENT_MAP.items():
            score = sum(1 for kw in keywords if kw in msg_lower)
            if score > 0:
                scores[tool] = score

        if scores:
            return max(scores, key=scores.get)

        # fallback to Gemini
        prompt = (
            f"User message: '{message}'\n"
            f"Choose one tool: medicine_reminder, emergency_detection, appointment_booking, "
            f"prescription_explainer, health_report, family_notifier, diet_recommendation, "
            f"exercise_coach, mood_companion, general_assistant\n"
            f"Reply with ONLY the tool name."
        )
        result = ask_gemini(prompt, fallback="general_assistant").strip().lower()
        for tool in INTENT_MAP:
            if tool in result:
                return tool
        return "general_assistant"

    # ── start a new flow ──────────────────────────────────────────────────────
    def start_flow(self, tool: str) -> str:
        self.current_tool = tool
        self.flow         = FLOWS.get(tool, [])
        self.flow_index   = 0
        self.collecting   = True if self.flow else False

        if not self.flow:
            return None  # no questions needed, act immediately

        # skip questions already answered
        while self.flow_index < len(self.flow):
            key, _ = self.flow[self.flow_index]
            if key in self.context:
                self.flow_index += 1
            else:
                break

        if self.flow_index >= len(self.flow):
            self.collecting = False
            return None

        _, question = self.flow[self.flow_index]
        return question

    # ── collect answer for current question ───────────────────────────────────
    def collect_answer(self, message: str) -> str | None:
        """
        Store answer, validate, move to next question.
        Returns next question string, or None if flow is complete.
        """
        if self.flow_index >= len(self.flow):
            self.collecting = False
            return None

        key, _ = self.flow[self.flow_index]

        # basic validations
        error = self._validate(key, message)
        if error:
            _, question = self.flow[self.flow_index]
            return f"{error}\n\n{question}"

        # store answer
        self.context[key] = message.strip()
        self.flow_index += 1

        # skip already-answered questions
        while self.flow_index < len(self.flow):
            next_key, _ = self.flow[self.flow_index]
            if next_key in self.context:
                self.flow_index += 1
            else:
                break

        if self.flow_index >= len(self.flow):
            self.collecting = False
            return None  # flow complete, ready to act

        _, next_question = self.flow[self.flow_index]
        return next_question

    def _validate(self, key: str, value: str) -> str | None:
        """Return error message or None if valid."""
        v = value.strip()
        if key == "age":
            try:
                age = int(re.search(r"\d+", v).group())
                if not (1 <= age <= 120):
                    return "Please enter a valid age between 1 and 120."
                self.context["age"] = str(age)
            except Exception:
                return "Please enter a valid age number."
        if key == "contact_number":
            digits = re.sub(r"\D", "", v)
            if len(digits) != 10:
                return "Please enter a valid 10-digit mobile number."
            self.context["contact_number"] = digits
        if key == "weight":
            try:
                float(re.search(r"[\d.]+", v).group())
            except Exception:
                return "Please enter a valid weight in kg. For example: 70"
        if key == "height":
            try:
                float(re.search(r"[\d.]+", v).group())
            except Exception:
                return "Please enter a valid height in cm. For example: 165"
        if key == "heart_rate":
            try:
                int(re.search(r"\d+", v).group())
            except Exception:
                return "Please enter a valid heart rate number. For example: 75"
        if key == "spo2":
            try:
                val = int(re.search(r"\d+", v).group())
                if not (50 <= val <= 100):
                    return "Please enter a valid SpO2 value between 50 and 100."
            except Exception:
                return "Please enter a valid SpO2 number. For example: 97"
        return None

    # ── ACT — call the tool ───────────────────────────────────────────────────
    def act(self) -> str:
        tool = self.current_tool
        ctx  = self.context

        if tool == "medicine_reminder":
            return tool_medicine_reminder(ctx.get("response", ""), ctx)
        elif tool == "emergency_detection":
            return tool_emergency_detection(ctx.get("_raw", ""), ctx)
        elif tool == "appointment_booking":
            return tool_appointment_booking(ctx.get("symptoms", ""), ctx)
        elif tool == "prescription_explainer":
            return tool_prescription_explainer(ctx.get("medicine_name", ""), ctx)
        elif tool == "health_report":
            return tool_health_report("", ctx)
        elif tool == "family_notifier":
            return tool_family_notifier("", ctx)
        elif tool == "diet_recommendation":
            return tool_diet_recommendation(ctx.get("condition", "General Wellness"), ctx)
        elif tool == "exercise_coach":
            return tool_exercise_coach(ctx.get("condition", "General Fitness"), ctx)
        elif tool == "mood_companion":
            return tool_mood_companion(ctx.get("mood", "") + " " + ctx.get("note", ""), ctx)
        else:
            return tool_general_assistant(ctx.get("_raw", ""), ctx)

    # ── RESPOND ───────────────────────────────────────────────────────────────
    def respond(self, message: str, is_question: bool = False) -> dict:
        self.history.append({"role": "agent", "content": message})
        self.turn += 1
        return {
            "message":     message,
            "tool_used":   TOOL_LABELS.get(self.current_tool, "Assistant"),
            "is_question": is_question,
            "context":     self.context.copy(),
        }

    # ── MAIN PROCESS LOOP ─────────────────────────────────────────────────────
    def process(self, user_message: str) -> dict:
        msg = self.perceive(user_message)
        self.context["_raw"] = msg

        # ── if already collecting answers ─────────────────────────────────────
        if self.collecting:
            next_q = self.collect_answer(msg)
            if next_q:
                return self.respond(next_q, is_question=True)
            else:
                # flow complete — act
                result = self.act()
                self._reset_flow()
                return self.respond(result, is_question=False)

        # ── new intent ────────────────────────────────────────────────────────
        # if current_tool already set by dashboard, use it; else detect
        tool = self.current_tool if self.current_tool else self.detect_intent(msg)
        self.current_tool = tool

        # emergency — act immediately, no questions
        if tool == "emergency_detection":
            result = tool_emergency_detection(msg, self.context)
            return self.respond(result, is_question=False)

        # general assistant — act immediately
        if tool == "general_assistant":
            result = tool_general_assistant(msg, self.context)
            return self.respond(result, is_question=False)

        # start question flow
        first_question = self.start_flow(tool)

        if first_question is None:
            # all info already in context, act immediately
            result = self.act()
            self._reset_flow()
            return self.respond(result, is_question=False)

        label = TOOL_LABELS.get(tool, "Assistant")
        intro = f"I will help you with {label}. Let me ask you a few questions.\n\n{first_question}"
        return self.respond(intro, is_question=True)

    def _reset_flow(self):
        self.flow       = []
        self.flow_index = 0
        self.collecting = False
        # keep context for memory across tools
