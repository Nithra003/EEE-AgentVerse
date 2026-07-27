# agent.py - ElderCare AI Appointment Booking Agent
#
# PERCEIVE -> THINK -> ACT -> RESPOND
# Simple plain English questions for elder citizens.
# Uses Gemini LLM for symptom analysis only.

import re
import google.generativeai as genai
from tools import find_specialist, check_available_slots, book_appointment, build_confirmation_text

STATE_GREETING    = "greeting"
STATE_GET_INFO    = "get_info"
STATE_ANALYSE     = "analyse"
STATE_SELECT_DOC  = "select_doctor"
STATE_SELECT_SLOT = "select_slot"
STATE_CONFIRM     = "confirm"
STATE_DONE        = "done"

EMERGENCY_KEYWORDS = [
    "unconscious", "not breathing", "heart attack", "stroke",
    "severe chest pain", "can't breathe", "collapsed", "bleeding heavily",
    "mayakkam", "moochu varavillai",
]


class AppointmentAgent:
    """
    AI Agent for appointment booking.
    - Simple plain English questions step by step.
    - Uses Gemini LLM for symptom analysis.
    - Falls back to weighted keyword tool if no API key.
    """

    def __init__(self, api_key: str = ""):
        self.api_key     = api_key
        self.state       = STATE_GREETING
        self.patient     = {}
        self.specialty   = None
        self.doctors     = []
        self.slots       = []
        self.appointment = None
        self.history     = []

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    # -----------------------------------------------------------------------
    # Main entry — PERCEIVE -> THINK -> ACT -> RESPOND
    # -----------------------------------------------------------------------
    def process(self, user_input: str) -> dict:
        user_input = user_input.strip()
        self.history.append({"role": "user", "content": user_input})

        if self._is_emergency(user_input):
            return self._emergency_response()

        if self.state == STATE_GREETING:
            response = self._handle_greeting()
        elif self.state == STATE_GET_INFO:
            response = self._handle_get_info(user_input)
        elif self.state == STATE_ANALYSE:
            response = self._handle_analyse()
        elif self.state == STATE_SELECT_DOC:
            response = self._handle_select_doctor(user_input)
        elif self.state == STATE_SELECT_SLOT:
            response = self._handle_select_slot(user_input)
        elif self.state == STATE_CONFIRM:
            response = self._handle_confirm(user_input)
        elif self.state == STATE_DONE:
            response = self._handle_done(user_input)
        else:
            response = self._respond("Type NEW to start over.")

        self.history.append({"role": "agent", "content": response["message"]})
        return response

    # -----------------------------------------------------------------------
    # State handlers
    # -----------------------------------------------------------------------
    def _handle_greeting(self) -> dict:
        self.state = STATE_GET_INFO
        return self._respond(
            "Hello! I am your ElderCare AI Agent.\n\n"
            "I will help you book a doctor appointment.\n\n"
            "Please enter your full name.",
            hint="Enter your full name"
        )

    def _handle_get_info(self, text: str) -> dict:

        if "name" not in self.patient:
            if len(text.strip()) < 2:
                return self._respond("Please enter a valid full name.")
            self.patient["name"] = text.strip().title()
            return self._respond(
                f"Thank you, {self.patient['name']}.\n\nHow old are you?",
                hint="Enter your age"
            )

        if "age" not in self.patient:
            age = self._extract_number(text)
            if not age or not (1 <= age <= 120):
                return self._respond("Please enter a valid age between 1 and 120.")
            self.patient["age"] = age
            return self._respond(
                "What is your gender?\n\nPlease type: Male, Female, or Other",
                hint="Male / Female / Other"
            )

        if "gender" not in self.patient:
            g = text.strip().lower()
            if g in ["m", "male"]:
                g = "male"
            elif g in ["f", "female"]:
                g = "female"
            elif g in ["other"]:
                g = "other"
            if g not in ["male", "female", "other"]:
                return self._respond("Please type Male, Female, or Other.")
            self.patient["gender"] = g.title()
            return self._respond(
                "What is your mobile number?\n\nPlease enter your 10-digit number.",
                hint="e.g. 9876543210"
            )

        if "phone" not in self.patient:
            phone = re.sub(r"[\s\-]", "", text)
            if not re.fullmatch(r"[6-9]\d{9}", phone):
                return self._respond(
                    "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
                )
            self.patient["phone"] = phone
            return self._respond(
                "What are your symptoms?\n\n"
                "Please describe how you are feeling.\n\n"
                "Example: I have chest pain and difficulty breathing.",
                hint="Describe your symptoms"
            )

        if "symptoms" not in self.patient:
            if len(text.strip()) < 3:
                return self._respond("Please describe your symptoms in a little more detail.")
            self.patient["symptoms"] = text.strip()
            self.state = STATE_ANALYSE
            return self._handle_analyse()

        if "date" not in self.patient:
            self.patient["date"] = text.strip()
            self.state = STATE_SELECT_SLOT
            return self._handle_select_slot_prompt()

        return self._respond("All information collected.")

    def _handle_analyse(self) -> dict:
        """THINK + ACT: Gemini or keyword tool analyses symptoms."""
        symptoms = self.patient.get("symptoms", "")

        if self.model:
            result = self._gemini_analyse(symptoms)
        else:
            result = find_specialist(symptoms)

        self.specialty = result["specialty"]
        self.doctors   = result["doctors"]

        doctor_list = "\n".join(
            f"  {i+1}. {d['name']} - {d['experience']}, Rating: {d['rating']}"
            for i, d in enumerate(result["doctor_details"])
        )

        self.state = STATE_SELECT_DOC
        return self._respond(
            f"Based on your symptoms, I recommend a {self.specialty}.\n\n"
            f"{result['description']}\n\n"
            f"Available doctors:\n{doctor_list}\n\n"
            f"Please type the number of the doctor you prefer.",
            hint="Type 1 or 2",
            data=result,
        )

    def _handle_select_doctor(self, text: str) -> dict:
        chosen = None
        num = self._extract_number(text)
        if num and 1 <= num <= len(self.doctors):
            chosen = self.doctors[num - 1]
        else:
            for name in self.doctors:
                if text.lower() in name.lower():
                    chosen = name
                    break

        if not chosen:
            opts = "\n".join(f"  {i+1}. {n}" for i, n in enumerate(self.doctors))
            return self._respond(f"Please choose a valid option:\n{opts}")

        self.patient["doctor"] = chosen
        slot_data  = check_available_slots(chosen)
        self.slots = slot_data["available"]

        self.state = STATE_SELECT_SLOT
        return self._respond(
            f"You have selected {chosen}.\n\n"
            f"What date would you like the appointment?\n\n"
            f"Example: 2026-08-15",
            hint="Enter date like 2026-08-15"
        )

    def _handle_select_slot_prompt(self) -> dict:
        slot_list = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(self.slots))
        return self._respond(
            f"Here are the available time slots:\n\n{slot_list}\n\n"
            f"Please type the number of your preferred time.",
            hint="Type a number e.g. 1"
        )

    def _handle_select_slot(self, text: str) -> dict:
        if "date" not in self.patient:
            self.patient["date"] = text.strip()
            return self._handle_select_slot_prompt()

        num = self._extract_number(text)
        if not num or not (1 <= num <= len(self.slots)):
            return self._respond(f"Please type a number between 1 and {len(self.slots)}.")

        self.patient["time"] = self.slots[num - 1]
        self.state = STATE_CONFIRM

        return self._respond(
            f"Please check your appointment details:\n\n"
            f"Name      : {self.patient['name']}\n"
            f"Age       : {self.patient['age']}\n"
            f"Gender    : {self.patient['gender']}\n"
            f"Phone     : {self.patient['phone']}\n"
            f"Symptoms  : {self.patient['symptoms']}\n"
            f"Doctor    : {self.patient['doctor']}\n"
            f"Specialty : {self.specialty}\n"
            f"Date      : {self.patient['date']}\n"
            f"Time      : {self.patient['time']}\n\n"
            f"Is everything correct?\n\nType YES to confirm or NO to cancel.",
            hint="YES or NO"
        )

    def _handle_confirm(self, text: str) -> dict:
        cmd = text.strip().upper()
        yes_words = ["YES", "CONFIRM", "OK", "SARI", "AAMA"]
        no_words  = ["NO", "CANCEL", "VENDA", "ILLAI"]

        if any(w in cmd for w in yes_words):
            self.appointment = book_appointment(
                patient   = self.patient,
                doctor    = self.patient["doctor"],
                specialty = self.specialty,
                date      = self.patient["date"],
                time      = self.patient["time"],
            )
            self.state = STATE_DONE
            return self._respond(
                f"Your appointment is confirmed!\n\n"
                f"Appointment ID: {self.appointment['apt_id']}\n\n"
                f"Please arrive 10 minutes early and carry a valid ID.\n\n"
                f"Type DOWNLOAD to save your confirmation.",
                hint="DOWNLOAD / NEW",
                data=self.appointment,
            )
        elif any(w in cmd for w in no_words):
            self.state   = STATE_GET_INFO
            self.patient = {}
            return self._respond("Booking cancelled.\n\nLet us start again. Please enter your full name.")
        else:
            return self._respond("Please type YES to confirm or NO to cancel.")

    def _handle_done(self, text: str) -> dict:
        cmd = text.strip().upper()
        if cmd == "DOWNLOAD" and self.appointment:
            return self._respond(
                "Your appointment confirmation is ready. Please click the button below to download.",
                data={
                    "download": build_confirmation_text(self.appointment),
                    "filename": f"{self.appointment['apt_id']}.txt"
                },
            )
        if cmd == "NEW":
            self.__init__(self.api_key)
            return self.process("start")
        return self._respond(
            "Type DOWNLOAD to save your confirmation.\n\nType NEW to book another appointment."
        )

    # -----------------------------------------------------------------------
    # Gemini symptom analysis (LLM used only here)
    # -----------------------------------------------------------------------
    def _gemini_analyse(self, symptoms: str) -> dict:
        try:
            from doctors import get_all_specialties, DOCTORS, SPECIALTY_INFO
            specialties = ", ".join(get_all_specialties())
            prompt = (
                f"Patient symptoms: \"{symptoms}\".\n"
                f"Available specialties: {specialties}.\n"
                "Reply in exactly two lines:\n"
                "Line 1: Best matching specialty (exact name from list).\n"
                "Line 2: Short patient-friendly reason (1 sentence, in English)."
            )
            response  = self.model.generate_content(prompt)
            lines     = [l.strip() for l in response.text.strip().splitlines() if l.strip()]
            specialty = lines[0] if lines else "General Physician"
            reason    = lines[1] if len(lines) > 1 else "Recommended based on your symptoms."

            if specialty not in get_all_specialties():
                raise ValueError("Unknown specialty")

            doctors = DOCTORS.get(specialty, DOCTORS["General Physician"])
            info    = SPECIALTY_INFO.get(specialty, {"icon": "🏥", "desc": ""})
            return {
                "specialty":      specialty,
                "confidence":     92,
                "icon":           info["icon"],
                "description":    reason,
                "doctors":        [d["name"] for d in doctors],
                "doctor_details": doctors,
            }
        except Exception:
            return find_specialist(symptoms)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _is_emergency(self, text: str) -> bool:
        return any(kw in text.lower() for kw in EMERGENCY_KEYWORDS)

    def _emergency_response(self) -> dict:
        return self._respond(
            "EMERGENCY ALERT\n\n"
            "Please call 108 immediately for an ambulance.\n\n"
            "Do not wait. Go to the nearest hospital emergency room right now.",
            emergency=True
        )

    def _extract_number(self, text: str):
        m = re.search(r"\d+", text)
        return int(m.group()) if m else None

    def _respond(self, message: str, hint: str = "", data: dict = None, emergency: bool = False) -> dict:
        return {
            "message":   message,
            "state":     self.state,
            "hint":      hint,
            "data":      data or {},
            "emergency": emergency,
        }

    def reset(self):
        self.__init__(self.api_key)
