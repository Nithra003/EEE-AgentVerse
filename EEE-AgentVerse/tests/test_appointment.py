"""
tests/test_appointment.py — Appointment booking tests (Agent-3 + Agent-11).
"""
from __future__ import annotations

import sys
from datetime import date, time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Agent-3-Appointment-Booking"))
sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-3 — Full appointment booking via tools.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent3Appointment:
    def setup_method(self):
        from tools import APPOINTMENTS
        APPOINTMENTS.clear()

    def test_book_appointment_returns_apt_id(self):
        from tools import book_appointment
        patient = {"name": "Rajan", "age": 68, "gender": "Male",
                   "phone": "9876543210", "symptoms": "chest pain"}
        record = book_appointment(patient, "Dr. Kumar Rajan", "Cardiologist",
                                  "2026-08-15", "09:00 AM")
        assert record["apt_id"].startswith("APT-")
        assert record["doctor"] == "Dr. Kumar Rajan"
        assert record["specialty"] == "Cardiologist"

    def test_book_appointment_stores_in_memory(self):
        from tools import book_appointment, APPOINTMENTS
        patient = {"name": "Alice", "age": 60, "gender": "Female",
                   "phone": "9876543210", "symptoms": "fever"}
        record = book_appointment(patient, "Dr. Priya", "General Physician",
                                  "2026-09-01", "10:00 AM")
        assert record["apt_id"] in APPOINTMENTS

    def test_multiple_bookings_unique_ids(self):
        from tools import book_appointment
        patient = {"name": "X", "age": 60, "gender": "Male",
                   "phone": "9876543210", "symptoms": "cold"}
        ids = set()
        for _ in range(5):
            r = book_appointment(patient, "Dr. X", "General Physician",
                                 "2026-08-15", "09:00 AM")
            ids.add(r["apt_id"])
        assert len(ids) == 5

    def test_check_slots_all_available_initially(self):
        from tools import check_available_slots, AVAILABLE_SLOTS
        result = check_available_slots("Dr. New Doctor")
        assert len(result["available"]) == len(AVAILABLE_SLOTS)
        assert result["booked"] == []

    def test_check_slots_reduces_after_booking(self):
        from tools import book_appointment, check_available_slots
        patient = {"name": "X", "age": 60, "gender": "Male",
                   "phone": "9876543210", "symptoms": "cold"}
        book_appointment(patient, "Dr. Slot", "General Physician",
                         "2026-08-15", "09:00 AM")
        result = check_available_slots("Dr. Slot")
        assert "09:00 AM" not in result["available"]

    def test_find_specialist_eye_symptoms(self):
        from tools import find_specialist
        result = find_specialist("blurred vision and eye pain")
        assert result["specialty"] == "Ophthalmologist"

    def test_find_specialist_skin_symptoms(self):
        from tools import find_specialist
        result = find_specialist("skin rash and eczema")
        assert result["specialty"] == "Dermatologist"

    def test_find_specialist_confidence_capped_at_95(self):
        from tools import find_specialist
        result = find_specialist(
            "chest pain heart attack cardiac palpitation angina "
            "breathless high bp hypertension"
        )
        assert result["confidence"] <= 95

    def test_build_confirmation_text_all_fields(self):
        from tools import build_confirmation_text
        apt = {
            "apt_id": "APT-20260101-1234", "name": "Rajan Kumar",
            "age": 68, "gender": "Male", "phone": "9876543210",
            "symptoms": "chest pain", "doctor": "Dr. Kumar Rajan",
            "specialty": "Cardiologist", "date": "2026-08-15",
            "time": "09:00 AM", "booked_at": "01 Jan 2026, 10:00 AM",
        }
        text = build_confirmation_text(apt)
        for field in ["APT-20260101-1234", "Rajan Kumar", "Dr. Kumar Rajan",
                      "Cardiologist", "2026-08-15", "9876543210"]:
            assert field in text

    def test_get_appointment_returns_correct_record(self):
        from tools import book_appointment, get_appointment
        patient = {"name": "Test", "age": 65, "gender": "Male",
                   "phone": "9876543210", "symptoms": "fever"}
        record = book_appointment(patient, "Dr. X", "General Physician",
                                  "2026-08-15", "09:00 AM")
        fetched = get_appointment(record["apt_id"])
        assert fetched["name"] == "Test"


# ═══════════════════════════════════════════════════════════════════════════════
# Agent-11 — appointment_service.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgent11AppointmentService:
    def test_generate_ref_format(self):
        from appointment.appointment_service import _generate_ref
        ref = _generate_ref()
        assert ref.startswith("APT-")
        parts = ref.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8   # YYYYMMDD
        assert len(parts[2]) == 5   # random alphanumeric

    def test_book_appointment_success(self):
        with patch("appointment.appointment_service.get_session") as mock_gs, \
             patch("appointment.appointment_service.repo") as mock_repo:
            mock_session = MagicMock()
            mock_gs.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_apt = MagicMock()
            mock_apt.id = 1
            mock_apt.apt_ref = "APT-20260101-ABCDE"
            mock_apt.doctor_name = "Dr. Kumar"
            mock_apt.specialty = "Cardiologist"
            mock_apt.hospital = "City Hospital"
            mock_apt.apt_date = date(2026, 8, 15)
            mock_apt.apt_time = time(9, 0)
            mock_apt.symptoms = "chest pain"
            mock_apt.status = "confirmed"
            mock_apt.notes = ""
            mock_apt.created_at = "2026-01-01"
            mock_repo.create_appointment.return_value = mock_apt
            from appointment.appointment_service import book_appointment
            result = book_appointment(
                user_id=1, doctor_name="Dr. Kumar",
                apt_date=date(2026, 8, 15), apt_time=time(9, 0),
                specialty="Cardiologist",
            )
        assert result is not None
        assert result["apt_ref"] == "APT-20260101-ABCDE"

    def test_book_appointment_db_error_returns_none(self):
        with patch("appointment.appointment_service.get_session",
                   side_effect=Exception("DB error")):
            from appointment.appointment_service import book_appointment
            result = book_appointment(
                user_id=1, doctor_name="Dr. X",
                apt_date=date(2026, 8, 15), apt_time=time(9, 0),
            )
        assert result is None

    def test_cancel_appointment_success(self):
        with patch("appointment.appointment_service.get_session") as mock_gs, \
             patch("appointment.appointment_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.cancel_appointment.return_value = True
            from appointment.appointment_service import cancel_appointment
            result = cancel_appointment(1)
        assert result is True

    def test_cancel_appointment_not_found(self):
        with patch("appointment.appointment_service.get_session") as mock_gs, \
             patch("appointment.appointment_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.cancel_appointment.return_value = False
            from appointment.appointment_service import cancel_appointment
            result = cancel_appointment(999)
        assert result is False

    def test_get_user_appointments_empty(self):
        with patch("appointment.appointment_service.get_session") as mock_gs, \
             patch("appointment.appointment_service.repo") as mock_repo:
            mock_gs.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_gs.return_value.__exit__ = MagicMock(return_value=False)
            mock_repo.get_appointments.return_value = []
            from appointment.appointment_service import get_user_appointments
            result = get_user_appointments(1)
        assert result == []

    def test_build_confirmation_text_agent11(self):
        from appointment.appointment_service import build_confirmation_text
        apt = {
            "apt_ref": "APT-TEST-ABCDE", "doctor_name": "Dr. Kumar",
            "specialty": "Cardiologist", "hospital": "City Hospital",
            "apt_date": "2026-08-15", "apt_time": "09:00 AM",
            "symptoms": "chest pain", "status": "confirmed",
        }
        text = build_confirmation_text(apt)
        assert "APT-TEST-ABCDE" in text
        assert "Dr. Kumar" in text
        assert "Cardiologist" in text

    def test_serialise_appointment(self):
        from appointment.appointment_service import _serialise
        mock_apt = MagicMock()
        mock_apt.id = 1
        mock_apt.apt_ref = "APT-TEST"
        mock_apt.doctor_name = "Dr. X"
        mock_apt.specialty = "General Physician"
        mock_apt.hospital = None
        mock_apt.apt_date = date(2026, 8, 15)
        mock_apt.apt_time = time(9, 0)
        mock_apt.symptoms = "fever"
        mock_apt.status = "confirmed"
        mock_apt.notes = None
        mock_apt.created_at = "2026-01-01"
        result = _serialise(mock_apt)
        assert result["apt_ref"] == "APT-TEST"
        assert result["hospital"] == "City Medical Centre"   # default
        assert result["notes"] == ""
