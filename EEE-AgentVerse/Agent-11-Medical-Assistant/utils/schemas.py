"""
utils/schemas.py — Pydantic v2 models for all data contracts.
Used for API-style validation at agent boundaries.
"""
from __future__ import annotations

from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ── User schemas ──────────────────────────────────────────────────────────────
class UserRegisterSchema(BaseModel):
    username:  str = Field(min_length=3, max_length=32)
    password:  str = Field(min_length=6)
    full_name: str = Field(min_length=2, max_length=128)
    age:       Optional[int] = Field(default=None, ge=1, le=120)
    gender:    Optional[str] = None
    phone:     Optional[str] = None
    language:  str = "en"

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        import re
        if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError("Username may only contain letters, digits, and underscores.")
        return v.lower()


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserProfileSchema(BaseModel):
    full_name: Optional[str] = None
    age:       Optional[int] = Field(default=None, ge=1, le=120)
    gender:    Optional[str] = None
    phone:     Optional[str] = None
    language:  Optional[str] = None
    theme:     Optional[str] = None


# ── Medicine schemas ──────────────────────────────────────────────────────────
class MedicineSchema(BaseModel):
    name:          str = Field(min_length=2, max_length=128)
    strength:      Optional[str] = None
    dosage:        Optional[str] = None
    frequency:     Optional[str] = None
    morning:       bool = False
    afternoon:     bool = False
    night:         bool = False
    before_food:   bool = False
    after_food:    bool = False
    duration_days: Optional[int] = Field(default=None, ge=1, le=3650)
    start_date:    Optional[date] = None
    end_date:      Optional[date] = None
    quantity:      Optional[int] = Field(default=None, ge=0)
    special_instr: Optional[str] = None

    @model_validator(mode="after")
    def end_after_start(self) -> "MedicineSchema":
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be on or after start_date.")
        return self


# ── Prescription schemas ──────────────────────────────────────────────────────
class ExtractedMedicineSchema(BaseModel):
    name:          str
    strength:      Optional[str] = None
    dosage:        Optional[str] = None
    frequency:     Optional[str] = None
    morning:       bool = False
    afternoon:     bool = False
    night:         bool = False
    before_food:   bool = False
    after_food:    bool = False
    duration_days: Optional[int] = None
    special_instr: Optional[str] = None
    confidence:    float = Field(default=0.5, ge=0.0, le=1.0)


class ExtractedPrescriptionSchema(BaseModel):
    doctor_name:    Optional[str] = None
    hospital_name:  Optional[str] = None
    date:           Optional[str] = None
    patient_name:   Optional[str] = None
    patient_age:    Optional[int] = None
    patient_gender: Optional[str] = None
    diagnosis:      Optional[str] = None
    special_notes:  Optional[str] = None
    medicines:      List[ExtractedMedicineSchema] = Field(default_factory=list)


# ── Reminder schemas ──────────────────────────────────────────────────────────
class ReminderCreateSchema(BaseModel):
    remind_time:  str                    # "HH:MM" or "HH:MM AM/PM"
    frequency:    str = "daily"          # daily | weekly | once
    medicine_id:  Optional[int] = None
    remind_date:  Optional[date] = None
    days_of_week: Optional[List[int]] = None   # 0=Mon … 6=Sun

    @field_validator("frequency")
    @classmethod
    def valid_frequency(cls, v: str) -> str:
        if v not in ("daily", "weekly", "once"):
            raise ValueError("frequency must be daily, weekly, or once.")
        return v


# ── Appointment schemas ───────────────────────────────────────────────────────
class AppointmentCreateSchema(BaseModel):
    doctor_name: str = Field(min_length=2)
    apt_date:    date
    apt_time:    str                     # "HH:MM AM/PM"
    specialty:   Optional[str] = None
    hospital:    Optional[str] = None
    symptoms:    Optional[str] = None
    notes:       Optional[str] = None

    @field_validator("apt_date")
    @classmethod
    def not_in_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Appointment date cannot be in the past.")
        return v
