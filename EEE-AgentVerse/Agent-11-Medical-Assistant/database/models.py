"""
database/models.py — All SQLAlchemy ORM table definitions.
Single file keeps all relationships visible in one place.
"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey,
    Index, Integer, String, Text, Time, UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all models."""
    pass


# ── Schema version (migration tracking) ──────────────────────────────────────
class SchemaVersion(Base):
    __tablename__ = "schema_versions"

    id:          Mapped[int]      = Column(Integer, primary_key=True, autoincrement=True)
    version:     Mapped[str]      = Column(String(32), unique=True, nullable=False)
    description: Mapped[str]      = Column(String(256), nullable=False, default="")
    applied_at:  Mapped[datetime] = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<SchemaVersion {self.version!r}>"


# ── Users ─────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("ix_users_username", "username", unique=True),
    )

    id:            Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    username:      Mapped[str]           = Column(String(32), unique=True, nullable=False)
    password_hash: Mapped[str]           = Column(String(128), nullable=False)
    full_name:     Mapped[str]           = Column(String(128), nullable=False)
    age:           Mapped[Optional[int]] = Column(Integer)
    gender:        Mapped[Optional[str]] = Column(String(16))
    phone:         Mapped[Optional[str]] = Column(String(20))
    language:      Mapped[str]           = Column(String(10), default="en", nullable=False)
    theme:         Mapped[str]           = Column(String(10), default="light", nullable=False)
    created_at:    Mapped[datetime]      = Column(DateTime, server_default=func.now())
    updated_at:    Mapped[Optional[datetime]] = Column(DateTime, onupdate=func.now())

    # Relationships
    prescriptions:        Mapped[List["Prescription"]]       = relationship(back_populates="user", cascade="all, delete-orphan")
    medicines:            Mapped[List["Medicine"]]           = relationship(back_populates="user", cascade="all, delete-orphan")
    reminders:            Mapped[List["Reminder"]]           = relationship(back_populates="user", cascade="all, delete-orphan")
    appointments:         Mapped[List["Appointment"]]        = relationship(back_populates="user", cascade="all, delete-orphan")
    conversation_history: Mapped[List["ConversationHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"


# ── Prescriptions ─────────────────────────────────────────────────────────────
class Prescription(Base):
    __tablename__ = "prescriptions"

    __table_args__ = (
        Index("ix_prescriptions_user_created", "user_id", "created_at"),
    )

    id:              Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    user_id:         Mapped[int]           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_path:      Mapped[Optional[str]] = Column(String(512))
    raw_ocr_text:    Mapped[Optional[str]] = Column(Text)
    ocr_engine:      Mapped[Optional[str]] = Column(String(32))
    ocr_confidence:  Mapped[Optional[float]] = Column(Float)
    doctor_name:     Mapped[Optional[str]] = Column(String(128))
    hospital_name:   Mapped[Optional[str]] = Column(String(256))
    rx_date:         Mapped[Optional[date]] = Column(Date)
    patient_name:    Mapped[Optional[str]] = Column(String(128))
    patient_age:     Mapped[Optional[int]] = Column(Integer)
    patient_gender:  Mapped[Optional[str]] = Column(String(16))
    diagnosis:       Mapped[Optional[str]] = Column(Text)
    special_notes:   Mapped[Optional[str]] = Column(Text)
    ai_model_used:   Mapped[Optional[str]] = Column(String(64))
    created_at:      Mapped[datetime]      = Column(DateTime, server_default=func.now())

    user:      Mapped["User"]          = relationship(back_populates="prescriptions")
    medicines: Mapped[List["Medicine"]] = relationship(back_populates="prescription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Prescription id={self.id} user_id={self.user_id}>"


# ── Medicines ─────────────────────────────────────────────────────────────────
class Medicine(Base):
    __tablename__ = "medicines"

    __table_args__ = (
        Index("ix_medicines_user_id", "user_id"),
        Index("ix_medicines_user_active", "user_id", "end_date"),
    )

    id:              Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[Optional[int]] = Column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"))
    user_id:         Mapped[int]           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name:            Mapped[str]           = Column(String(128), nullable=False)
    strength:        Mapped[Optional[str]] = Column(String(64))
    dosage:          Mapped[Optional[str]] = Column(String(64))
    frequency:       Mapped[Optional[str]] = Column(String(64))
    morning:         Mapped[bool]          = Column(Boolean, default=False, nullable=False)
    afternoon:       Mapped[bool]          = Column(Boolean, default=False, nullable=False)
    night:           Mapped[bool]          = Column(Boolean, default=False, nullable=False)
    before_food:     Mapped[bool]          = Column(Boolean, default=False, nullable=False)
    after_food:      Mapped[bool]          = Column(Boolean, default=False, nullable=False)
    duration_days:   Mapped[Optional[int]] = Column(Integer)
    start_date:      Mapped[Optional[date]] = Column(Date)
    end_date:        Mapped[Optional[date]] = Column(Date)
    quantity:        Mapped[Optional[int]] = Column(Integer)
    special_instr:   Mapped[Optional[str]] = Column(Text)
    confidence:      Mapped[Optional[float]] = Column(Float)
    created_at:      Mapped[datetime]      = Column(DateTime, server_default=func.now())

    user:         Mapped["User"]           = relationship(back_populates="medicines")
    prescription: Mapped[Optional["Prescription"]] = relationship(back_populates="medicines")
    reminders:    Mapped[List["Reminder"]]  = relationship(back_populates="medicine", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Medicine id={self.id} name={self.name!r}>"


# ── Reminders ─────────────────────────────────────────────────────────────────
class Reminder(Base):
    __tablename__ = "reminders"

    __table_args__ = (
        Index("ix_reminders_user_status", "user_id", "status"),
        Index("ix_reminders_user_time", "user_id", "remind_time"),
    )

    id:               Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id:      Mapped[Optional[int]] = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"))
    user_id:          Mapped[int]           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    remind_time:      Mapped[time]          = Column(Time, nullable=False)
    remind_date:      Mapped[Optional[date]] = Column(Date)
    frequency:        Mapped[str]           = Column(String(32), default="daily", nullable=False)
    days_of_week:     Mapped[Optional[str]] = Column(String(64))   # JSON: "[0,4]" = Mon,Fri
    status:           Mapped[str]           = Column(String(16), default="active", nullable=False)
    snooze_until:     Mapped[Optional[datetime]] = Column(DateTime)
    scheduler_job_id: Mapped[Optional[str]] = Column(String(128))
    created_at:       Mapped[datetime]      = Column(DateTime, server_default=func.now())

    user:     Mapped["User"]              = relationship(back_populates="reminders")
    medicine: Mapped[Optional["Medicine"]] = relationship(back_populates="reminders")
    logs:     Mapped[List["ReminderLog"]]  = relationship(back_populates="reminder", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Reminder id={self.id} status={self.status!r}>"


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    __table_args__ = (
        Index("ix_reminder_logs_reminder_action", "reminder_id", "action"),
        Index("ix_reminder_logs_fired_at", "fired_at"),
    )

    id:          Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    reminder_id: Mapped[int]           = Column(Integer, ForeignKey("reminders.id", ondelete="CASCADE"), nullable=False)
    fired_at:    Mapped[datetime]      = Column(DateTime, nullable=False)
    action:      Mapped[str]           = Column(String(16), nullable=False)   # taken|missed|snoozed|skipped
    note:        Mapped[Optional[str]] = Column(Text)

    reminder: Mapped["Reminder"] = relationship(back_populates="logs")


# ── Appointments ──────────────────────────────────────────────────────────────
class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        Index("ix_appointments_user_date", "user_id", "apt_date"),
        Index("ix_appointments_user_status", "user_id", "status"),
        UniqueConstraint("apt_ref", name="uq_appointments_apt_ref"),
    )

    id:          Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    user_id:     Mapped[int]           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    apt_ref:     Mapped[str]           = Column(String(32), unique=True, nullable=False)
    doctor_name: Mapped[str]           = Column(String(128), nullable=False)
    specialty:   Mapped[Optional[str]] = Column(String(64))
    hospital:    Mapped[Optional[str]] = Column(String(256))
    apt_date:    Mapped[date]          = Column(Date, nullable=False)
    apt_time:    Mapped[time]          = Column(Time, nullable=False)
    symptoms:    Mapped[Optional[str]] = Column(Text)
    status:      Mapped[str]           = Column(String(16), default="confirmed", nullable=False)
    notes:       Mapped[Optional[str]] = Column(Text)
    created_at:  Mapped[datetime]      = Column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} ref={self.apt_ref!r}>"


# ── Conversation History ──────────────────────────────────────────────────────
class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    __table_args__ = (
        Index("ix_conv_user_session", "user_id", "session_id"),
        Index("ix_conv_session_created", "session_id", "created_at"),
    )

    id:         Mapped[int]           = Column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]           = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str]           = Column(String(64), nullable=False)
    role:       Mapped[str]           = Column(String(16), nullable=False)   # user|assistant
    content:    Mapped[str]           = Column(Text, nullable=False)
    language:   Mapped[Optional[str]] = Column(String(10))
    agent_type: Mapped[Optional[str]] = Column(String(32))   # prescription|appointment|reminder|chat
    created_at: Mapped[datetime]      = Column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="conversation_history")

    def __repr__(self) -> str:
        return f"<ConversationHistory id={self.id} role={self.role!r}>"
