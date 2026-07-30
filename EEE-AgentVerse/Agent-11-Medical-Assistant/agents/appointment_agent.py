"""
agents/appointment_agent.py — FSM-based appointment booking agent.
States: GREET → GET_INFO → ANALYSE → SELECT_DOC → SELECT_SLOT → CONFIRM → DONE
Supports language kwarg; never raises unexpected keyword argument errors.
"""
from __future__ import annotations

import re
from datetime import date, time
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentResponse, BaseAgent
from ai.llm_router import get_router
from ai.prompt_templates import SYMPTOM_ANALYSE
from appointment.appointment_service import book_appointment, build_confirmation_text
from appointment.doctor_registry import (
    EMERGENCY_KEYWORDS, SPECIALTY_INFO,
    find_specialist, get_all_specialties, get_available_slots,
    DOCTORS,
)
from utils.date_utils import parse_date, parse_time
from utils.logger import get_logger
from utils.validators import validate_age, validate_phone

log = get_logger(__name__)

# ── FSM states ────────────────────────────────────────────────────────────────
_GREET       = "greet"
_GET_INFO    = "get_info"
_ANALYSE     = "analyse"
_SELECT_DOC  = "select_doc"
_SELECT_SLOT = "select_slot"
_CONFIRM     = "confirm"
_DONE        = "done"

_YES = {"yes", "y", "confirm", "ok", "sure", "sari", "aama", "ha", "haan"}
_NO  = {"no", "n", "cancel", "venda", "illai", "nahi"}


class AppointmentAgent(BaseAgent):
    """
    Multi-step appointment booking agent.
    Accepts language, model, database kwargs for forward compatibility.
    """

    def __init__(
        self,
        user_id: Optional[int] = None,
        language: str = "en",
        session_id: Optional[str] = None,
        model: Optional[str] = None,       # accepted, not used (router handles it)
        database: Optional[Any] = None,    # accepted, not used (engine handles it)
        **kwargs: Any,                     # absorb any future kwargs gracefully
    ) -> None:
        super().__init__(user_id=user_id, language=language, session_id=session_id)
        self._state:       str             = _GREET
        self._patient:     Dict[str, Any]  = {}
        self._specialty:   Optional[str]   = None
        self._doctors:     List[str]       = []
        self._slots:       List[str]       = []
        self._appointment: Optional[Dict]  = None

    # ── Public entry point ────────────────────────────────────────────────────
    def process(self, user_input: str) -> AgentResponse:
        text = (user_input or "").strip()

        if self._is_emergency(text):
            return self._emergency()

        handlers = {
            _GREET:       self._handle_greet,
            _GET_INFO:    self._handle_get_info,
            _ANALYSE:     self._handle_analyse,
            _SELECT_DOC:  self._handle_select_doc,
            _SELECT_SLOT: self._handle_select_slot,
            _CONFIRM:     self._handle_confirm,
            _DONE:        self._handle_done,
        }
        handler = handlers.get(self._state, self._handle_done)
        try:
            return handler(text)
        except Exception as exc:
            log.error("AppointmentAgent.process error: %s", exc)
            return AgentResponse(
                message="Something went wrong. Please type NEW to start over.",
                success=False,
            )

    def reset(self) -> None:
        self._state      = _GREET
        self._patient    = {}
        self._specialty  = None
        self._doctors    = []
        self._slots      = []
        self._appointment = None

    # ── State handlers ────────────────────────────────────────────────────────
    def _handle_greet(self, _: str) -> AgentResponse:
        self._state = _GET_INFO
        return AgentResponse(
            message=(
                "Hello! I am your AI Appointment Assistant. 👋\n\n"
                "I will help you book a doctor appointment step by step.\n\n"
                "Please enter your **full name** to begin."
            ),
            hint="Enter your full name",
        )

    def _handle_get_info(self, text: str) -> AgentResponse:
        p = self._patient

        if "name" not in p:
            if len(text) < 2:
                return AgentResponse(message="Please enter a valid full name.", success=False)
            p["name"] = text.title()
            return AgentResponse(message=f"Thank you, {p['name']}! 😊\n\nHow old are you?", hint="Enter your age")

        if "age" not in p:
            ok, err = validate_age(text)
            if not ok:
                return AgentResponse(message=err, success=False)
            p["age"] = int(re.search(r"\d+", text).group())
            return AgentResponse(message="What is your gender?\n\nType: **Male**, **Female**, or **Other**", hint="Male / Female / Other")

        if "gender" not in p:
            g = text.strip().lower()
            mapping = {"m": "Male", "male": "Male", "f": "Female", "female": "Female", "other": "Other"}
            if g not in mapping:
                return AgentResponse(message="Please type Male, Female, or Other.", success=False)
            p["gender"] = mapping[g]
            return AgentResponse(message="What is your **phone number**?", hint="e.g. 9876543210")

        if "phone" not in p:
            ok, err = validate_phone(text)
            if not ok:
                return AgentResponse(message=err, success=False)
            p["phone"] = re.sub(r"[\s\-\(\)]", "", text)
            return AgentResponse(
                message=(
                    "Please describe your **symptoms** in detail.\n\n"
                    "_Example: I have chest pain and difficulty breathing._"
                ),
                hint="Describe your symptoms",
            )

        if "symptoms" not in p:
            if len(text) < 3:
                return AgentResponse(message="Please describe your symptoms in a little more detail.", success=False)
            p["symptoms"] = text
            self._state = _ANALYSE
            return self._handle_analyse("")

        return AgentResponse(message="All information collected.", success=True)

    def _handle_analyse(self, _: str) -> AgentResponse:
        symptoms = self._patient.get("symptoms", "")
        result   = self._analyse_symptoms(symptoms)

        self._specialty = result["specialty"]
        self._doctors   = result["doctors"]

        doctor_list = "\n".join(
            f"  **{i+1}.** {d['name']} — {d['experience']}, ⭐ {d['rating']}"
            for i, d in enumerate(result["doctor_details"])
        )
        self._state = _SELECT_DOC
        return AgentResponse(
            message=(
                f"{result['icon']} Based on your symptoms, I recommend a **{self._specialty}**.\n\n"
                f"_{result['description']}_\n\n"
                f"**Available Doctors:**\n{doctor_list}\n\n"
                f"Please type the **number** of the doctor you prefer."
            ),
            hint="Type 1 or 2",
            data=result,
        )

    def _handle_select_doc(self, text: str) -> AgentResponse:
        num = self._extract_number(text)
        chosen = None

        if num and 1 <= num <= len(self._doctors):
            chosen = self._doctors[num - 1]
        else:
            for name in self._doctors:
                if text.lower() in name.lower():
                    chosen = name
                    break

        if not chosen:
            opts = "\n".join(f"  {i+1}. {n}" for i, n in enumerate(self._doctors))
            return AgentResponse(message=f"Please choose a valid option:\n{opts}", success=False)

        self._patient["doctor"] = chosen
        self._slots = get_available_slots(chosen)

        slot_list = "\n".join(f"  **{i+1}.** {s}" for i, s in enumerate(self._slots))
        self._state = _SELECT_SLOT
        return AgentResponse(
            message=(
                f"You selected **{chosen}**. ✅\n\n"
                f"What **date** would you like the appointment?\n\n"
                f"_Example: 2026-08-15_"
            ),
            hint="Enter date like 2026-08-15",
        )

    def _handle_select_slot(self, text: str) -> AgentResponse:
        if "date" not in self._patient:
            d = parse_date(text)
            if not d or d < date.today():
                return AgentResponse(message="Please enter a valid future date (YYYY-MM-DD).", success=False)
            self._patient["date"] = d
            slot_list = "\n".join(f"  **{i+1}.** {s}" for i, s in enumerate(self._slots))
            return AgentResponse(
                message=f"**Available time slots:**\n\n{slot_list}\n\nPlease type the **number** of your preferred time.",
                hint="Type a number e.g. 1",
            )

        num = self._extract_number(text)
        if not num or not (1 <= num <= len(self._slots)):
            return AgentResponse(message=f"Please type a number between 1 and {len(self._slots)}.", success=False)

        self._patient["time"] = self._slots[num - 1]
        self._state = _CONFIRM

        p = self._patient
        return AgentResponse(
            message=(
                f"**Please confirm your appointment:**\n\n"
                f"👤 Name      : {p['name']}\n"
                f"🎂 Age       : {p['age']}\n"
                f"⚧ Gender    : {p['gender']}\n"
                f"📱 Phone     : {p['phone']}\n"
                f"🩺 Symptoms  : {p['symptoms']}\n"
                f"👨‍⚕️ Doctor    : {p['doctor']}\n"
                f"🏥 Specialty : {self._specialty}\n"
                f"📅 Date      : {p['date']}\n"
                f"⏰ Time      : {p['time']}\n\n"
                f"Type **YES** to confirm or **NO** to cancel."
            ),
            hint="YES or NO",
        )

    def _handle_confirm(self, text: str) -> AgentResponse:
        cmd = text.strip().lower()
        if cmd in _YES:
            p   = self._patient
            apt = book_appointment(
                user_id=self.user_id or 0,
                doctor_name=p["doctor"],
                apt_date=p["date"],
                apt_time=parse_time(p["time"]) or time(9, 0),
                specialty=self._specialty,
                symptoms=p.get("symptoms"),
            )
            if not apt:
                return AgentResponse(message="Booking failed. Please try again.", success=False)

            self._appointment = apt
            self._state = _DONE
            return AgentResponse(
                message=(
                    f"🎉 **Appointment Confirmed!**\n\n"
                    f"Reference: `{apt['apt_ref']}`\n\n"
                    f"Please arrive 10 minutes early with a valid ID.\n\n"
                    f"Type **DOWNLOAD** to save your confirmation."
                ),
                hint="DOWNLOAD / NEW",
                data=apt,
            )
        elif cmd in _NO:
            self.reset()
            self._state = _GET_INFO
            return AgentResponse(message="Booking cancelled. Let's start again.\n\nPlease enter your full name.")
        else:
            return AgentResponse(message="Please type **YES** to confirm or **NO** to cancel.", success=False)

    def _handle_done(self, text: str) -> AgentResponse:
        cmd = text.strip().upper()
        if cmd == "DOWNLOAD" and self._appointment:
            return AgentResponse(
                message="Your confirmation is ready. Click below to download.",
                data={
                    "download": build_confirmation_text(self._appointment),
                    "filename": f"{self._appointment['apt_ref']}.txt",
                },
            )
        if cmd == "NEW":
            self.reset()
            return self.process("start")
        return AgentResponse(
            message="Type **DOWNLOAD** to save your confirmation or **NEW** to book another appointment."
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _analyse_symptoms(self, symptoms: str) -> Dict:
        """Try LLM analysis; fall back to keyword matching."""
        router = get_router()
        if router.is_any_available():
            try:
                prompt = SYMPTOM_ANALYSE.render_user(
                    symptoms=symptoms,
                    age=self._patient.get("age", "unknown"),
                    gender=self._patient.get("gender", "unknown"),
                )
                raw = router.chat(SYMPTOM_ANALYSE.system, prompt)
                lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
                specialty = lines[0] if lines else "General Physician"
                reason    = lines[1] if len(lines) > 1 else "Recommended based on your symptoms."

                if specialty in get_all_specialties():
                    doctors = DOCTORS.get(specialty, DOCTORS["General Physician"])
                    info    = SPECIALTY_INFO.get(specialty)
                    return {
                        "specialty":      specialty,
                        "confidence":     90,
                        "icon":           info.icon if info else "🏥",
                        "description":    reason,
                        "doctors":        [d.name for d in doctors],
                        "doctor_details": [d._asdict() for d in doctors],
                    }
            except Exception as exc:
                log.warning("LLM symptom analysis failed: %s — using keyword fallback", exc)

        return find_specialist(symptoms)

    def _is_emergency(self, text: str) -> bool:
        return any(kw in text.lower() for kw in EMERGENCY_KEYWORDS)

    def _emergency(self) -> AgentResponse:
        return AgentResponse(
            message=(
                "🚨 **EMERGENCY DETECTED**\n\n"
                "Please call **108** (ambulance) immediately.\n\n"
                "Do not wait — go to the nearest hospital emergency room right now."
            ),
            emergency=True,
        )

    @staticmethod
    def _extract_number(text: str) -> Optional[int]:
        m = re.search(r"\d+", text)
        return int(m.group()) if m else None
