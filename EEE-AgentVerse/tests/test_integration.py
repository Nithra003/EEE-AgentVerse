"""
tests/test_integration.py — Integration tests: multi-step flows across modules.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in [
    str(ROOT / "Agent-3-Appointment-Booking"),
    str(ROOT / "Agent-1-Medicine-Reminder"),
    str(ROOT / "Agent-4-Prescription-Explainer"),
    str(ROOT / "Agent-11-Medical-Assistant"),
]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — Full booking flow (no Ollama, no Gemini)
# ═══════════════════════════════════════════════════════════════════════════════

class TestFullBookingFlow:
    def _agent(self):
        with patch("ai_engine.AIEngine._check_ollama", return_value=False):
            from agent import AppointmentAgent
            return AppointmentAgent()

    def _fill_patient(self, agent):
        agent.process("start")
        agent.process("Rajan Kumar")
        agent.process("68")
        agent.process("Male")
        agent.process("9876543210")

    def test_full_flow_to_confirm(self):
        agent = self._agent()
        self._fill_patient(agent)
        resp = agent.process("chest pain and shortness of breath")
        # AI engine falls back to keyword — should recommend Cardiologist
        assert agent.state in ("select_doctor", "analyse")

    def test_full_flow_confirm_yes_books_appointment(self):
        from tools import APPOINTMENTS
        APPOINTMENTS.clear()
        agent = self._agent()
        self._fill_patient(agent)
        agent.process("chest pain")
        # Force state to confirm with all data
        agent.state = "confirm"
        agent.patient.update({
            "doctor": "Dr. Kumar Rajan",
            "date": "2026-08-15",
            "time": "09:00 AM",
        })
        agent.specialty = "Cardiologist"
        with patch("agent.appointment_to_voice"):
            resp = agent._handle_confirm("YES")
        assert agent.state == "done"
        assert agent.appointment is not None
        assert agent.appointment["apt_id"].startswith("APT-")
        APPOINTMENTS.clear()

    def test_full_flow_confirm_no_resets(self):
        agent = self._agent()
        agent.state = "confirm"
        agent.patient = {"name": "X", "age": 60, "gender": "Male",
                         "phone": "9876543210", "symptoms": "fever",
                         "doctor": "Dr. X", "date": "2026-01-01", "time": "09:00 AM"}
        agent.specialty = "General Physician"
        agent._handle_confirm("NO")
        assert agent.state == "get_info"
        assert agent.patient == {}

    def test_doctor_selection_by_number(self):
        agent = self._agent()
        self._fill_patient(agent)
        agent.process("fever and cold")
        if agent.state == "select_doctor":
            agent.doctors = ["Dr. Priya Sharma", "Dr. Arjun Mehta"]
            resp = agent._handle_select_doctor("1")
            assert agent.patient.get("doctor") == "Dr. Priya Sharma"

    def test_slot_selection_stores_time(self):
        agent = self._agent()
        agent.state = "select_slot"
        agent.patient = {"name": "X", "age": 60, "gender": "Male",
                         "phone": "9876543210", "symptoms": "fever",
                         "doctor": "Dr. X", "date": "2026-01-01"}
        agent.slots = ["09:00 AM", "10:00 AM", "11:30 AM"]
        resp = agent._handle_select_slot("2")
        assert agent.patient.get("time") == "10:00 AM"

    def test_new_command_resets_agent(self):
        agent = self._agent()
        agent.state = "done"
        agent.patient = {"name": "X"}
        with patch("ai_engine.AIEngine._check_ollama", return_value=False):
            resp = agent._handle_done("NEW")
        assert agent.state == "get_info"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-1 — Medicine reminder adherence flow
# ═══════════════════════════════════════════════════════════════════════════════

class TestMedicineReminderFlow:
    def setup_method(self):
        import medicine_db
        medicine_db._LOG.clear()

    def test_log_and_retrieve_multiple_doses(self):
        from medicine_db import log_dose, get_log
        for status in ["taken", "taken", "missed", "taken"]:
            log_dose("Rajan", "Metformin", status)
        logs = get_log("Rajan")
        assert len(logs) == 4

    def test_adherence_100_percent(self):
        from medicine_db import log_dose, get_adherence
        for _ in range(5):
            log_dose("Perfect", "Aspirin", "taken")
        stats = get_adherence("Perfect")
        assert stats["percentage"] == 100

    def test_adherence_0_percent(self):
        from medicine_db import log_dose, get_adherence
        for _ in range(3):
            log_dose("Worst", "Insulin", "missed")
        stats = get_adherence("Worst")
        assert stats["percentage"] == 0

    def test_todays_log_filters_correctly(self):
        from medicine_db import log_dose, get_todays_log
        log_dose("Today", "Paracetamol", "taken")
        logs = get_todays_log("Today")
        assert len(logs) >= 1

    def test_missed_count_per_medicine(self):
        from medicine_db import log_dose, check_missed_count
        log_dose("P", "Metformin", "missed")
        log_dose("P", "Metformin", "taken")
        log_dose("P", "Aspirin", "missed")
        assert check_missed_count("P", "Metformin") == 1
        assert check_missed_count("P", "Aspirin") == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — AI engine keyword fallback integration
# ═══════════════════════════════════════════════════════════════════════════════

class TestAIEngineIntegration:
    def _engine(self):
        with patch("ai_engine.AIEngine._check_ollama", return_value=False):
            from ai_engine import AIEngine
            return AIEngine()

    def test_analyse_symptoms_no_ollama_uses_keyword(self):
        engine = self._engine()
        result = engine.analyse_symptoms("chest pain and palpitation", age=70, gender="male")
        assert result["specialty"] == "Cardiologist"
        assert "doctors" in result
        assert "doctor_details" in result

    def test_analyse_symptoms_skin_rash(self):
        engine = self._engine()
        result = engine.analyse_symptoms("skin rash and itching", age=65, gender="female")
        assert result["specialty"] == "Dermatologist"

    def test_analyse_symptoms_unknown_defaults_general(self):
        engine = self._engine()
        result = engine.analyse_symptoms("xyz unknown", age=60, gender="male")
        assert result["specialty"] == "General Physician"

    def test_explain_prescription_no_ollama_returns_safe(self):
        engine = self._engine()
        result = engine.explain_prescription("Paracetamol 500mg twice daily", age=65)
        assert "summary" in result
        assert isinstance(result["summary"], str)

    def test_memory_add_and_clear(self):
        engine = self._engine()
        engine.add_to_memory("user", "I have fever")
        engine.add_to_memory("agent", "Please see a doctor")
        assert engine.memory.summary() != ""
        engine.clear_memory()
        assert engine.memory.summary() == ""

    def test_parse_json_valid(self):
        engine = self._engine()
        result = engine._parse_json('{"specialty": "Cardiologist", "confidence": 90}')
        assert result["specialty"] == "Cardiologist"

    def test_parse_json_with_markdown_fences(self):
        engine = self._engine()
        result = engine._parse_json('```json\n{"specialty": "Dentist"}\n```')
        assert result["specialty"] == "Dentist"

    def test_parse_json_invalid_returns_none(self):
        engine = self._engine()
        assert engine._parse_json("not json at all") is None
        assert engine._parse_json("") is None

    def test_valid_specialty_true(self):
        engine = self._engine()
        assert engine._valid_specialty("Cardiologist") is True

    def test_valid_specialty_false(self):
        engine = self._engine()
        assert engine._valid_specialty("Astrologer") is False

    def test_active_model_fallback_label(self):
        engine = self._engine()
        assert engine.active_model == "keyword-fallback"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — utils.py Gemini fallback integration
# ═══════════════════════════════════════════════════════════════════════════════

class TestGeminiUtilsIntegration:
    def test_recommend_specialty_gemini_fallback_on_error(self):
        from utils import recommend_specialty_gemini
        with patch("utils.genai.configure"), \
             patch("utils.genai.GenerativeModel", side_effect=Exception("API error")):
            specialty, explanation, confidence = recommend_specialty_gemini(
                "chest pain", "fake-key"
            )
        assert specialty in ["Cardiologist", "General Physician"]
        assert isinstance(confidence, int)

    def test_keyword_fallback_direct(self):
        from utils import _keyword_fallback
        spec, conf = _keyword_fallback("tooth pain and gum bleeding")
        assert spec == "Dentist"
        assert conf > 0

    def test_keyword_fallback_unknown(self):
        from utils import _keyword_fallback
        spec, conf = _keyword_fallback("xyz unknown")
        assert spec == "General Physician"
        assert conf == 40

    def test_build_confirmation_text_utils(self):
        from utils import build_confirmation_text
        details = {
            "apt_id": "APT-TEST", "name": "Rajan", "age": 68,
            "gender": "Male", "phone": "9876543210", "symptoms": "fever",
            "doctor": "Dr. X", "specialty": "General Physician",
            "date": "2026-08-15", "time": "09:00 AM",
        }
        text = build_confirmation_text(details)
        assert "APT-TEST" in text
        assert "Rajan" in text
