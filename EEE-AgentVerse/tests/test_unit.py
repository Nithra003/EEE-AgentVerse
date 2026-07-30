"""
tests/test_unit.py — Unit tests for all agents and shared utilities.
Target: 95% coverage of pure-logic functions (no I/O, no external services).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in [
    str(ROOT / "Agent-3-Appointment-Booking"),
    str(ROOT / "Agent-1-Medicine-Reminder"),
    str(ROOT / "Agent-4-Prescription-Explainer"),
    str(ROOT / "Agent-10-Voice-Assistant"),
    str(ROOT / "Agent-11-Medical-Assistant"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — doctors.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestDoctors:
    def test_get_all_specialties_returns_list(self):
        from doctors import get_all_specialties
        specs = get_all_specialties()
        assert isinstance(specs, list)
        assert len(specs) >= 6

    def test_known_specialties_present(self):
        from doctors import get_all_specialties
        specs = get_all_specialties()
        for s in ["Cardiologist", "General Physician", "Orthopedic", "Dentist"]:
            assert s in specs

    def test_get_doctors_for_specialty_known(self):
        from doctors import get_doctors_for_specialty
        docs = get_doctors_for_specialty("Cardiologist")
        assert len(docs) >= 1
        assert "name" in docs[0]
        assert "experience" in docs[0]
        assert "rating" in docs[0]

    def test_get_doctors_for_specialty_unknown_falls_back(self):
        from doctors import get_doctors_for_specialty, DOCTORS
        docs = get_doctors_for_specialty("Unknown Specialty")
        assert docs == DOCTORS["General Physician"]

    def test_available_slots_not_empty(self):
        from doctors import AVAILABLE_SLOTS
        assert len(AVAILABLE_SLOTS) >= 5

    def test_symptom_map_has_weights(self):
        from doctors import SYMPTOM_MAP
        for spec, levels in SYMPTOM_MAP.items():
            assert "high" in levels
            assert "medium" in levels
            assert "low" in levels

    def test_specialty_info_has_icon_and_desc(self):
        from doctors import SPECIALTY_INFO
        for spec, info in SPECIALTY_INFO.items():
            assert "icon" in info
            assert "desc" in info


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — tools.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestTools:
    def test_find_specialist_chest_pain(self):
        from tools import find_specialist
        result = find_specialist("chest pain and shortness of breath")
        assert result["specialty"] == "Cardiologist"
        assert result["confidence"] > 0
        assert len(result["doctors"]) >= 1

    def test_find_specialist_tooth_pain(self):
        from tools import find_specialist
        result = find_specialist("severe toothache and gum bleeding")
        assert result["specialty"] == "Dentist"

    def test_find_specialist_unknown_defaults_general(self):
        from tools import find_specialist
        result = find_specialist("xyz abc unknown symptom")
        assert result["specialty"] == "General Physician"
        assert result["confidence"] == 40

    def test_find_specialist_returns_doctor_details(self):
        from tools import find_specialist
        result = find_specialist("fever and cold")
        assert "doctor_details" in result
        assert isinstance(result["doctor_details"], list)

    def test_check_available_slots_returns_slots(self):
        from tools import check_available_slots
        result = check_available_slots("Dr. Test")
        assert "available" in result
        assert "booked" in result
        assert isinstance(result["available"], list)

    def test_book_appointment_creates_record(self):
        from tools import book_appointment, get_appointment
        patient = {"name": "Test User", "age": 65, "gender": "Male",
                   "phone": "9876543210", "symptoms": "fever"}
        record = book_appointment(patient, "Dr. Priya Sharma", "General Physician",
                                  "2026-08-15", "09:00 AM")
        assert record["apt_id"].startswith("APT-")
        assert record["name"] == "Test User"
        assert get_appointment(record["apt_id"]) == record

    def test_get_appointment_missing_returns_none(self):
        from tools import get_appointment
        assert get_appointment("APT-NONEXISTENT") is None

    def test_build_confirmation_text_contains_fields(self):
        from tools import build_confirmation_text
        apt = {
            "apt_id": "APT-20260101-1234", "name": "Rajan", "age": 68,
            "gender": "Male", "phone": "9876543210", "symptoms": "fever",
            "doctor": "Dr. Priya", "specialty": "General Physician",
            "date": "2026-08-15", "time": "09:00 AM",
            "booked_at": "01 Jan 2026, 10:00 AM",
        }
        text = build_confirmation_text(apt)
        assert "APT-20260101-1234" in text
        assert "Rajan" in text
        assert "Dr. Priya" in text
        assert "General Physician" in text

    def test_check_available_slots_excludes_booked(self):
        from tools import book_appointment, check_available_slots, APPOINTMENTS
        APPOINTMENTS.clear()
        patient = {"name": "A", "age": 60, "gender": "Male",
                   "phone": "9876543210", "symptoms": "cold"}
        book_appointment(patient, "Dr. Slot Test", "General Physician",
                         "2026-08-15", "09:00 AM")
        result = check_available_slots("Dr. Slot Test")
        assert "09:00 AM" not in result["available"]
        assert "09:00 AM" in result["booked"]
        APPOINTMENTS.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — utils.py (validation)
# ═══════════════════════════════════════════════════════════════════════════════

class TestUtils:
    def test_validate_name_valid(self):
        from utils import validate_name
        assert validate_name("Rajan Kumar") is None

    def test_validate_name_empty(self):
        from utils import validate_name
        assert validate_name("") is not None
        assert validate_name("  ") is not None

    def test_validate_name_too_short(self):
        from utils import validate_name
        assert validate_name("A") is not None

    def test_validate_age_valid(self):
        from utils import validate_age
        assert validate_age(65) is None
        assert validate_age(1) is None
        assert validate_age(120) is None

    def test_validate_age_invalid(self):
        from utils import validate_age
        assert validate_age(0) is not None
        assert validate_age(121) is not None
        assert validate_age("abc") is not None

    def test_validate_phone_valid(self):
        from utils import validate_phone
        assert validate_phone("9876543210") is None
        assert validate_phone("6543210987") is None

    def test_validate_phone_invalid(self):
        from utils import validate_phone
        assert validate_phone("1234567890") is not None   # starts with 1
        assert validate_phone("98765") is not None         # too short
        assert validate_phone("abcdefghij") is not None

    def test_validate_symptoms_valid(self):
        from utils import validate_symptoms
        assert validate_symptoms("chest pain") is None

    def test_validate_symptoms_empty(self):
        from utils import validate_symptoms
        assert validate_symptoms("") is not None
        assert validate_symptoms("   ") is not None

    def test_validate_all_returns_errors(self):
        from utils import validate_all
        errors = validate_all({})
        assert len(errors) > 0

    def test_validate_all_valid_form(self):
        from utils import validate_all
        form = {
            "name": "Rajan Kumar", "age": 65, "phone": "9876543210",
            "symptoms": "fever", "date": "2026-08-15",
            "time": "09:00 AM", "doctor": "Dr. Priya",
        }
        assert validate_all(form) == []

    def test_generate_appointment_id_format(self):
        from utils import generate_appointment_id
        apt_id = generate_appointment_id()
        assert apt_id.startswith("APT-")
        assert len(apt_id) > 10


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-1 — medicine_db.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestMedicineDB:
    def setup_method(self):
        import medicine_db
        medicine_db._LOG.clear()

    def test_get_medicine_known(self):
        from medicine_db import get_medicine
        med = get_medicine("metformin")
        assert med is not None
        assert med["name"] == "Metformin"
        assert med["type"] == "Diabetes"

    def test_get_medicine_case_insensitive(self):
        from medicine_db import get_medicine
        assert get_medicine("PARACETAMOL") is not None
        assert get_medicine("Aspirin") is not None

    def test_get_medicine_unknown_returns_none(self):
        from medicine_db import get_medicine
        assert get_medicine("unknownxyz") is None

    def test_get_generic_returns_dict(self):
        from medicine_db import get_generic
        result = get_generic("SomeDrug")
        assert result["name"] == "Somedrug"
        assert "missed_advice" in result

    def test_log_dose_and_get_log(self):
        from medicine_db import log_dose, get_log
        log_dose("Rajan", "Metformin", "taken")
        logs = get_log("Rajan")
        assert len(logs) == 1
        assert logs[0]["status"] == "taken"

    def test_get_log_filters_by_patient(self):
        from medicine_db import log_dose, get_log
        log_dose("Alice", "Aspirin", "taken")
        log_dose("Bob", "Insulin", "missed")
        assert all(l["patient"] == "Alice" for l in get_log("Alice"))
        assert all(l["patient"] == "Bob" for l in get_log("Bob"))

    def test_get_adherence_calculates_percentage(self):
        from medicine_db import log_dose, get_adherence
        log_dose("TestPat", "Metformin", "taken")
        log_dose("TestPat", "Metformin", "taken")
        log_dose("TestPat", "Metformin", "missed")
        stats = get_adherence("TestPat")
        assert stats["total"] == 3
        assert stats["taken"] == 2
        assert stats["missed"] == 1
        assert stats["percentage"] == 67

    def test_get_adherence_empty(self):
        from medicine_db import get_adherence
        stats = get_adherence("NoPatient")
        assert stats["percentage"] == 0

    def test_check_missed_count(self):
        from medicine_db import log_dose, check_missed_count
        log_dose("P1", "Insulin", "missed")
        log_dose("P1", "Insulin", "missed")
        log_dose("P1", "Insulin", "taken")
        assert check_missed_count("P1", "Insulin") == 2

    def test_medicine_has_required_fields(self):
        from medicine_db import MEDICINES
        required = {"name", "type", "food", "water", "missed_advice",
                    "skip_risk", "interactions", "emergency_symptoms"}
        for name, data in MEDICINES.items():
            assert required.issubset(data.keys()), f"{name} missing fields"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-4 — ocr_engine.py field extraction
# ═══════════════════════════════════════════════════════════════════════════════

class TestOCRFieldExtraction:
    def test_extract_fields_doctor(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Dr. Priya Sharma\nCity Hospital\nDate: 12/06/2025")
        assert fields["doctor"] == "Priya Sharma"

    def test_extract_fields_hospital(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Apollo Hospital: Chennai\nPatient: Rajan")
        assert "Apollo" in fields["hospital"] or "Chennai" in fields["hospital"]

    def test_extract_fields_date(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Date: 12/06/2025\nSome text")
        assert "2025" in fields["date"] or "12" in fields["date"]

    def test_extract_fields_patient(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Patient: Rajan Kumar\nTab Paracetamol 500mg")
        assert fields["patient"] == "Rajan Kumar"

    def test_extract_fields_dosage(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Tab Paracetamol 500mg twice daily")
        assert "500mg" in fields["dosage"]

    def test_extract_fields_frequency(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Tab Metformin 500mg twice daily 30 days")
        assert any("twice" in f.lower() or "daily" in f.lower()
                   for f in fields["frequency"])

    def test_extract_fields_duration(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Tab Aspirin 75mg once daily 30 days")
        assert any("30" in d for d in fields["duration"])

    def test_extract_fields_instructions(self):
        from ocr_engine import _extract_fields
        fields = _extract_fields("Tab Metformin 500mg after food")
        assert any("after food" in i.lower() for i in fields["instructions"])

    def test_score_fields_range(self):
        from ocr_engine import _score_fields
        fields = {"doctor": "Dr. X", "hospital": "", "date": "12/06/2025",
                  "patient": "Rajan", "medicines": ["Tab Para"], "dosage": ["500mg"],
                  "frequency": ["twice daily"], "duration": ["5 days"],
                  "instructions": ["after food"]}
        score = _score_fields(fields, 0.8)
        assert 0.0 <= score <= 1.0

    def test_extract_prescription_empty_bytes_returns_safe(self):
        from ocr_engine import extract_prescription
        result = extract_prescription(b"not-an-image", max_retries=0)
        assert "error" in result or result["confidence"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-10 — chatbot.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestChatbot:
    def test_get_wellness_suggestions_known_mood(self):
        from chatbot import get_wellness_suggestions
        suggestions = get_wellness_suggestions("Happy")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_get_wellness_suggestions_unknown_mood_fallback(self):
        from chatbot import get_wellness_suggestions
        suggestions = get_wellness_suggestions("UnknownMood")
        assert isinstance(suggestions, list)

    def test_get_daily_motivation_returns_string(self):
        from chatbot import get_daily_motivation
        quote = get_daily_motivation()
        assert isinstance(quote, str)
        assert len(quote) > 5

    def test_generate_ai_response_empty_message(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value=""):
            result = generate_ai_response("Rajan", "", "Normal")
        assert "Rajan" in result or "friend" in result.lower()

    def test_generate_ai_response_gemini_fallback(self):
        from chatbot import generate_ai_response
        with patch("chatbot.ask_gemini", return_value="unavailable"):
            result = generate_ai_response("Rajan", "I feel sad", "Sad")
        assert isinstance(result, str)
        assert len(result) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — AppointmentAgent state machine
# ═══════════════════════════════════════════════════════════════════════════════

class TestAppointmentAgentUnit:
    def _make_agent(self):
        with patch("ai_engine.AIEngine._check_ollama", return_value=False):
            from agent import AppointmentAgent
            return AppointmentAgent()

    def test_initial_state_is_greeting(self):
        agent = self._make_agent()
        assert agent.state == "greeting"

    def test_process_start_transitions_to_get_info(self):
        agent = self._make_agent()
        resp = agent.process("start")
        assert agent.state == "get_info"
        assert "name" in resp["message"].lower()

    def test_emergency_keywords_trigger_emergency(self):
        agent = self._make_agent()
        agent.process("start")
        resp = agent.process("I am unconscious and not breathing")
        assert resp["emergency"] is True
        assert "108" in resp["message"]

    def test_emergency_tamil_keywords(self):
        agent = self._make_agent()
        agent.process("start")
        resp = agent.process("mayakkam irukku")
        assert resp["emergency"] is True

    def test_name_collection(self):
        agent = self._make_agent()
        agent.process("start")
        resp = agent.process("Rajan Kumar")
        assert agent.patient.get("name") == "Rajan Kumar"
        assert "age" in resp["message"].lower()

    def test_name_too_short_rejected(self):
        agent = self._make_agent()
        agent.process("start")
        resp = agent.process("A")
        assert "name" in resp["message"].lower()
        assert "name" not in agent.patient

    def test_age_valid(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        resp = agent.process("68")
        assert agent.patient.get("age") == 68

    def test_age_invalid_rejected(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        resp = agent.process("200")
        assert "age" not in agent.patient

    def test_gender_male_accepted(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        agent.process("68")
        resp = agent.process("Male")
        assert agent.patient.get("gender") == "Male"

    def test_gender_invalid_rejected(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        agent.process("68")
        resp = agent.process("unknown_gender")
        assert "gender" not in agent.patient

    def test_phone_valid(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        agent.process("68")
        agent.process("Male")
        resp = agent.process("9876543210")
        assert agent.patient.get("phone") == "9876543210"

    def test_phone_invalid_rejected(self):
        agent = self._make_agent()
        agent.process("start")
        agent.process("Rajan Kumar")
        agent.process("68")
        agent.process("Male")
        resp = agent.process("1234567890")
        assert "phone" not in agent.patient

    def test_extract_number_helper(self):
        agent = self._make_agent()
        assert agent._extract_number("option 2") == 2
        assert agent._extract_number("no number here") is None

    def test_respond_structure(self):
        agent = self._make_agent()
        resp = agent._respond("Hello", hint="test", emergency=False)
        assert "message" in resp
        assert "state" in resp
        assert "hint" in resp
        assert "data" in resp
        assert "emergency" in resp

    def test_is_emergency_true(self):
        agent = self._make_agent()
        assert agent._is_emergency("severe chest pain") is True
        assert agent._is_emergency("heart attack") is True

    def test_is_emergency_false(self):
        agent = self._make_agent()
        assert agent._is_emergency("I have a mild headache") is False

    def test_confirm_no_resets_state(self):
        agent = self._make_agent()
        agent.state = "confirm"
        agent.patient = {"name": "X", "age": 60, "gender": "Male",
                         "phone": "9876543210", "symptoms": "fever",
                         "doctor": "Dr. X", "date": "2026-01-01", "time": "09:00 AM"}
        agent.specialty = "General Physician"
        resp = agent._handle_confirm("NO")
        assert agent.state == "get_info"
        assert agent.patient == {}

    def test_done_state_download(self):
        agent = self._make_agent()
        agent.state = "done"
        agent.appointment = {
            "apt_id": "APT-TEST-1234", "name": "X", "age": 60,
            "gender": "Male", "phone": "9876543210", "symptoms": "fever",
            "doctor": "Dr. X", "specialty": "General Physician",
            "date": "2026-01-01", "time": "09:00 AM",
            "booked_at": "01 Jan 2026, 10:00 AM",
        }
        resp = agent._handle_done("DOWNLOAD")
        assert "download" in resp["data"]

    def test_reset_clears_state(self):
        agent = self._make_agent()
        agent.patient = {"name": "X"}
        agent.reset()
        assert agent.patient == {}
        assert agent.state == "greeting"
