# appointment/__init__.py
from appointment.appointment_service import (
    book_appointment, cancel_appointment,
    get_user_appointments, build_confirmation_text,
)
from appointment.doctor_registry import (
    find_specialist, get_all_specialties,
    get_available_slots, DOCTORS, SPECIALTY_INFO,
    EMERGENCY_KEYWORDS,
)

__all__ = [
    "book_appointment", "cancel_appointment",
    "get_user_appointments", "build_confirmation_text",
    "find_specialist", "get_all_specialties",
    "get_available_slots", "DOCTORS", "SPECIALTY_INFO",
    "EMERGENCY_KEYWORDS",
]
