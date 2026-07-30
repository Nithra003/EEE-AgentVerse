"""
tests/test_database.py — Database layer tests (Agent-11 models + repository).
Uses in-memory SQLite — no file I/O, no external services.
"""
from __future__ import annotations

import sys
from datetime import date, time, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Agent-11-Medical-Assistant"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ── In-memory DB fixture ──────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def db_session():
    from database.models import Base
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Models — repr and basic construction
# ═══════════════════════════════════════════════════════════════════════════════

class TestModels:
    def test_user_repr(self, db_session):
        from database.models import User
        u = User(username="testuser", password_hash="abc", full_name="Test User")
        assert "testuser" in repr(u)

    def test_prescription_repr(self, db_session):
        from database.models import Prescription
        p = Prescription(user_id=1)
        assert "Prescription" in repr(p)

    def test_medicine_repr(self, db_session):
        from database.models import Medicine
        m = Medicine(user_id=1, name="Paracetamol")
        assert "Paracetamol" in repr(m)

    def test_reminder_repr(self, db_session):
        from database.models import Reminder
        r = Reminder(user_id=1, remind_time=time(8, 0), status="active")
        assert "active" in repr(r)

    def test_appointment_repr(self, db_session):
        from database.models import Appointment
        a = Appointment(user_id=1, apt_ref="APT-TEST",
                        doctor_name="Dr. X", apt_date=date(2026, 8, 15),
                        apt_time=time(9, 0))
        assert "APT-TEST" in repr(a)

    def test_conversation_history_repr(self, db_session):
        from database.models import ConversationHistory
        c = ConversationHistory(user_id=1, session_id="sess1",
                                role="user", content="hello")
        assert "user" in repr(c)


# ═══════════════════════════════════════════════════════════════════════════════
# Repository — User CRUD
# ═══════════════════════════════════════════════════════════════════════════════

class TestUserRepository:
    def test_hash_password_deterministic(self):
        from database.repository import hash_password
        h1 = hash_password("secret")
        h2 = hash_password("secret")
        assert h1 == h2
        assert len(h1) == 64   # SHA-256 hex

    def test_hash_password_different_inputs(self):
        from database.repository import hash_password
        assert hash_password("abc") != hash_password("xyz")

    def test_create_and_get_user(self, db_session):
        from database.repository import create_user, get_user_by_username
        user = create_user(db_session, "alice_test", "pass123", "Alice Test", age=65)
        db_session.commit()
        found = get_user_by_username(db_session, "alice_test")
        assert found is not None
        assert found.full_name == "Alice Test"
        assert found.age == 65

    def test_create_user_lowercase_username(self, db_session):
        from database.repository import create_user, get_user_by_username
        create_user(db_session, "UPPER_USER", "pass", "Upper User")
        db_session.commit()
        found = get_user_by_username(db_session, "upper_user")
        assert found is not None

    def test_authenticate_user_correct_password(self, db_session):
        from database.repository import create_user, authenticate_user
        create_user(db_session, "auth_user", "correct_pass", "Auth User")
        db_session.commit()
        result = authenticate_user(db_session, "auth_user", "correct_pass")
        assert result is not None

    def test_authenticate_user_wrong_password(self, db_session):
        from database.repository import authenticate_user
        result = authenticate_user(db_session, "auth_user", "wrong_pass")
        assert result is None

    def test_authenticate_user_nonexistent(self, db_session):
        from database.repository import authenticate_user
        result = authenticate_user(db_session, "nobody", "pass")
        assert result is None

    def test_update_user_profile(self, db_session):
        from database.repository import create_user, update_user_profile
        user = create_user(db_session, "update_user", "pass", "Update User", age=60)
        db_session.commit()
        updated = update_user_profile(db_session, user.id, age=70, language="ta")
        db_session.commit()
        assert updated.age == 70
        assert updated.language == "ta"

    def test_update_user_profile_nonexistent(self, db_session):
        from database.repository import update_user_profile
        result = update_user_profile(db_session, 99999, age=70)
        assert result is None

    def test_get_user_by_username_not_found(self, db_session):
        from database.repository import get_user_by_username
        result = get_user_by_username(db_session, "nonexistent_xyz")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# Repository — Medicine CRUD
# ═══════════════════════════════════════════════════════════════════════════════

class TestMedicineRepository:
    @pytest.fixture
    def user_id(self, db_session):
        from database.repository import create_user
        user = create_user(db_session, "med_test_user", "pass", "Med Test", age=65)
        db_session.commit()
        return user.id

    def test_create_medicine(self, db_session, user_id):
        from database.repository import create_medicine
        med = create_medicine(db_session, user_id=user_id, name="Metformin",
                              strength="500mg", morning=True)
        db_session.commit()
        assert med.id is not None
        assert med.name == "Metformin"

    def test_get_medicines(self, db_session, user_id):
        from database.repository import create_medicine, get_medicines
        create_medicine(db_session, user_id=user_id, name="Aspirin")
        db_session.commit()
        meds = get_medicines(db_session, user_id)
        assert any(m.name == "Aspirin" for m in meds)

    def test_get_active_medicines_excludes_expired(self, db_session, user_id):
        from database.repository import create_medicine, get_active_medicines
        from datetime import date, timedelta
        past = date.today() - timedelta(days=10)
        create_medicine(db_session, user_id=user_id, name="ExpiredDrug",
                        end_date=past)
        db_session.commit()
        active = get_active_medicines(db_session, user_id)
        assert not any(m.name == "ExpiredDrug" for m in active)

    def test_update_medicine(self, db_session, user_id):
        from database.repository import create_medicine, update_medicine
        med = create_medicine(db_session, user_id=user_id, name="OldName")
        db_session.commit()
        updated = update_medicine(db_session, med.id, name="NewName")
        db_session.commit()
        assert updated.name == "NewName"

    def test_update_medicine_not_found(self, db_session):
        from database.repository import update_medicine
        result = update_medicine(db_session, 99999, name="X")
        assert result is None

    def test_delete_medicine(self, db_session, user_id):
        from database.repository import create_medicine, delete_medicine, get_medicine
        med = create_medicine(db_session, user_id=user_id, name="ToDelete")
        db_session.commit()
        result = delete_medicine(db_session, med.id)
        db_session.commit()
        assert result is True
        assert get_medicine(db_session, med.id) is None

    def test_delete_medicine_not_found(self, db_session):
        from database.repository import delete_medicine
        result = delete_medicine(db_session, 99999)
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Repository — Reminder CRUD
# ═══════════════════════════════════════════════════════════════════════════════

class TestReminderRepository:
    @pytest.fixture
    def user_id(self, db_session):
        from database.repository import create_user
        user = create_user(db_session, "rem_test_user", "pass", "Rem Test", age=70)
        db_session.commit()
        return user.id

    def test_create_reminder(self, db_session, user_id):
        from database.repository import create_reminder
        rem = create_reminder(db_session, user_id=user_id,
                              remind_time=time(8, 0), frequency="daily")
        db_session.commit()
        assert rem.id is not None
        assert rem.status == "active"

    def test_get_reminders_by_status(self, db_session, user_id):
        from database.repository import create_reminder, get_reminders
        create_reminder(db_session, user_id=user_id,
                        remind_time=time(9, 0), frequency="daily")
        db_session.commit()
        active = get_reminders(db_session, user_id, status="active")
        assert len(active) >= 1

    def test_update_reminder_status(self, db_session, user_id):
        from database.repository import create_reminder, update_reminder_status
        rem = create_reminder(db_session, user_id=user_id,
                              remind_time=time(10, 0), frequency="daily")
        db_session.commit()
        updated = update_reminder_status(db_session, rem.id, "paused")
        db_session.commit()
        assert updated.status == "paused"

    def test_log_reminder_action(self, db_session, user_id):
        from database.repository import create_reminder, log_reminder_action
        rem = create_reminder(db_session, user_id=user_id,
                              remind_time=time(11, 0), frequency="daily")
        db_session.commit()
        log = log_reminder_action(db_session, rem.id, "taken", "on time")
        db_session.commit()
        assert log.action == "taken"

    def test_count_missed(self, db_session, user_id):
        from database.repository import create_reminder, log_reminder_action, count_missed
        rem = create_reminder(db_session, user_id=user_id,
                              remind_time=time(12, 0), frequency="daily")
        db_session.commit()
        log_reminder_action(db_session, rem.id, "missed")
        log_reminder_action(db_session, rem.id, "missed")
        log_reminder_action(db_session, rem.id, "taken")
        db_session.commit()
        assert count_missed(db_session, rem.id) == 2

    def test_get_adherence_stats(self, db_session, user_id):
        from database.repository import create_reminder, log_reminder_action, get_adherence_stats
        rem = create_reminder(db_session, user_id=user_id,
                              remind_time=time(14, 0), frequency="daily")
        db_session.commit()
        for action in ["taken", "taken", "missed"]:
            log_reminder_action(db_session, rem.id, action)
        db_session.commit()
        stats = get_adherence_stats(db_session, user_id)
        assert "taken" in stats
        assert "missed" in stats
        assert "percentage" in stats
        assert 0 <= stats["percentage"] <= 100


# ═══════════════════════════════════════════════════════════════════════════════
# Repository — Appointment CRUD
# ═══════════════════════════════════════════════════════════════════════════════

class TestAppointmentRepository:
    @pytest.fixture
    def user_id(self, db_session):
        from database.repository import create_user
        user = create_user(db_session, "apt_test_user", "pass", "Apt Test", age=68)
        db_session.commit()
        return user.id

    def test_create_appointment(self, db_session, user_id):
        from database.repository import create_appointment
        apt = create_appointment(
            db_session, user_id=user_id, apt_ref="APT-DB-TEST-001",
            doctor_name="Dr. Kumar", apt_date=date(2026, 8, 15),
            apt_time=time(9, 0), specialty="Cardiologist",
        )
        db_session.commit()
        assert apt.id is not None
        assert apt.apt_ref == "APT-DB-TEST-001"

    def test_get_appointments(self, db_session, user_id):
        from database.repository import create_appointment, get_appointments
        create_appointment(
            db_session, user_id=user_id, apt_ref="APT-DB-TEST-002",
            doctor_name="Dr. X", apt_date=date(2026, 9, 1), apt_time=time(10, 0),
        )
        db_session.commit()
        apts = get_appointments(db_session, user_id)
        assert len(apts) >= 1

    def test_get_appointment_by_ref(self, db_session, user_id):
        from database.repository import create_appointment, get_appointment_by_ref
        create_appointment(
            db_session, user_id=user_id, apt_ref="APT-DB-TEST-003",
            doctor_name="Dr. Y", apt_date=date(2026, 10, 1), apt_time=time(11, 0),
        )
        db_session.commit()
        found = get_appointment_by_ref(db_session, "APT-DB-TEST-003")
        assert found is not None
        assert found.doctor_name == "Dr. Y"

    def test_cancel_appointment(self, db_session, user_id):
        from database.repository import create_appointment, cancel_appointment
        apt = create_appointment(
            db_session, user_id=user_id, apt_ref="APT-DB-TEST-004",
            doctor_name="Dr. Z", apt_date=date(2026, 11, 1), apt_time=time(14, 0),
        )
        db_session.commit()
        result = cancel_appointment(db_session, apt.id)
        db_session.commit()
        assert result is True
        assert apt.status == "cancelled"

    def test_cancel_appointment_not_found(self, db_session):
        from database.repository import cancel_appointment
        result = cancel_appointment(db_session, 99999)
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# Repository — Conversation history
# ═══════════════════════════════════════════════════════════════════════════════

class TestConversationRepository:
    @pytest.fixture
    def user_id(self, db_session):
        from database.repository import create_user
        user = create_user(db_session, "conv_test_user", "pass", "Conv Test", age=65)
        db_session.commit()
        return user.id

    def test_add_and_get_conversation(self, db_session, user_id):
        from database.repository import add_conversation_turn, get_conversation
        add_conversation_turn(db_session, user_id=user_id, session_id="sess-001",
                              role="user", content="Hello")
        add_conversation_turn(db_session, user_id=user_id, session_id="sess-001",
                              role="assistant", content="Hi there!")
        db_session.commit()
        turns = get_conversation(db_session, user_id, "sess-001")
        assert len(turns) >= 2

    def test_conversation_session_isolation(self, db_session, user_id):
        from database.repository import add_conversation_turn, get_conversation
        add_conversation_turn(db_session, user_id=user_id, session_id="sess-A",
                              role="user", content="Session A message")
        add_conversation_turn(db_session, user_id=user_id, session_id="sess-B",
                              role="user", content="Session B message")
        db_session.commit()
        turns_a = get_conversation(db_session, user_id, "sess-A")
        turns_b = get_conversation(db_session, user_id, "sess-B")
        assert all(t.session_id == "sess-A" for t in turns_a)
        assert all(t.session_id == "sess-B" for t in turns_b)


# ═══════════════════════════════════════════════════════════════════════════════
# DatabaseManager
# ═══════════════════════════════════════════════════════════════════════════════

class TestDatabaseManager:
    def test_health_check_passes(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        dm.init_db()
        assert dm.health_check() is True

    def test_stats_structure(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        stats = dm.stats()
        assert "healthy" in stats
        assert "sessions_opened" in stats
        assert "sessions_active" in stats

    def test_session_counts_increment(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        dm.init_db()
        before = dm.stats()["sessions_opened"]
        with dm.session() as s:
            assert s is not None
        assert dm.stats()["sessions_opened"] == before + 1

    def test_integrity_check_passes_on_fresh_db(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        dm.init_db()
        # In-memory DB returns None for file path — should return True
        result = dm.integrity_check()
        assert result is True

    def test_backup_skipped_for_memory_db(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        result = dm.backup()
        assert result is None   # no file path

    def test_db_file_path_memory_returns_none(self):
        from database.engine import DatabaseManager
        dm = DatabaseManager("sqlite:///:memory:")
        assert dm._db_file_path() is None

    def test_db_file_path_file_returns_path(self, tmp_path):
        from database.engine import DatabaseManager
        db_file = tmp_path / "test.db"
        dm = DatabaseManager(f"sqlite:///{db_file}")
        result = dm._db_file_path()
        assert result == db_file
