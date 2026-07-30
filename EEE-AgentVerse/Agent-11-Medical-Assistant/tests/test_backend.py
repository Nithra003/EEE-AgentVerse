"""
tests/test_backend.py — Smoke tests for all backend modules.
Run: python -m pytest tests/ -v
No external services required for most tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import date, time


# ── Config ────────────────────────────────────────────────────────────────────
def test_config_imports():
    from config import DATABASE_URL, LLM_MODELS, OCR_CONFIDENCE_THRESHOLD
    assert DATABASE_URL.startswith("sqlite:///")
    assert len(LLM_MODELS) == 3
    assert 0 < OCR_CONFIDENCE_THRESHOLD < 1


# ── Utils ─────────────────────────────────────────────────────────────────────
def test_validators():
    from utils.validators import (
        validate_username, validate_password, validate_age,
        validate_phone, validate_medicine_name,
    )
    assert validate_username("john_doe")[0] is True
    assert validate_username("ab")[0] is False
    assert validate_password("secret")[0] is True
    assert validate_password("abc")[0] is False
    assert validate_age(65)[0] is True
    assert validate_age(0)[0] is False
    assert validate_phone("9876543210")[0] is True
    assert validate_medicine_name("Paracetamol")[0] is True


def test_date_utils():
    from utils.date_utils import parse_date, parse_time, friendly_date, days_until
    assert parse_date("2025-12-31") == date(2025, 12, 31)
    assert parse_date("31/12/2025") == date(2025, 12, 31)
    assert parse_time("08:00") == time(8, 0)
    assert parse_time("08:00 AM") == time(8, 0)
    assert isinstance(friendly_date(date.today()), str)


def test_error_handler():
    from utils.error_handler import safe_execute

    @safe_execute(fallback="fallback_value")
    def always_fails():
        raise RuntimeError("boom")

    result = always_fails()
    assert result == "fallback_value"


# ── Database ──────────────────────────────────────────────────────────────────
def test_db_init():
    from database.engine import init_db, get_session
    init_db()
    with get_session() as session:
        assert session is not None


def test_user_crud():
    from database.engine import init_db, get_session
    from database import repository as repo

    init_db()
    username = "test_user_smoke"

    with get_session() as session:
        # Clean up from previous run
        existing = repo.get_user_by_username(session, username)
        if existing:
            session.delete(existing)

    with get_session() as session:
        user = repo.create_user(session, username, "password123", "Test User", age=65)
        assert user.id is not None
        assert user.username == username

    with get_session() as session:
        found = repo.get_user_by_username(session, username)
        assert found is not None
        assert found.full_name == "Test User"

    with get_session() as session:
        auth = repo.authenticate_user(session, username, "password123")
        assert auth is not None
        bad  = repo.authenticate_user(session, username, "wrongpass")
        assert bad is None


def test_medicine_crud():
    from database.engine import init_db, get_session
    from database import repository as repo

    init_db()
    with get_session() as session:
        user = repo.get_user_by_username(session, "test_user_smoke")
        if not user:
            user = repo.create_user(session, "test_user_smoke2", "pw", "Test2", age=70)
        uid = user.id

    with get_session() as session:
        med = repo.create_medicine(session, user_id=uid, name="Paracetamol", strength="500mg", morning=True)
        assert med.id is not None
        assert med.name == "Paracetamol"

    with get_session() as session:
        meds = repo.get_medicines(session, uid)
        assert any(m.name == "Paracetamol" for m in meds)


# ── OCR ───────────────────────────────────────────────────────────────────────
def test_ocr_pipeline_import():
    from ocr.ocr_pipeline import OCRPipeline
    pipeline = OCRPipeline()
    assert pipeline is not None


def test_image_preprocessor():
    from ocr.image_preprocessor import preprocess_standard
    from PIL import Image
    import io

    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    result = preprocess_standard(buf.getvalue())
    assert isinstance(result, bytes)
    assert len(result) > 0


# ── AI ────────────────────────────────────────────────────────────────────────
def test_llm_router_import():
    from ai.llm_router import get_router
    router = get_router()
    assert router is not None
    assert isinstance(router.active_model_name, str)


def test_prompt_templates():
    from ai.prompt_templates import PRESCRIPTION_EXTRACT, MEDICINE_EXPLAIN
    rendered = PRESCRIPTION_EXTRACT.render_user(ocr_text="Dr. Smith\nParacetamol 500mg")
    assert "Paracetamol" in rendered
    assert "json" in rendered.lower()


# ── Translation ───────────────────────────────────────────────────────────────
def test_language_detection():
    from translation.language_detector import detect_language
    result = detect_language("Hello, how are you feeling today?")
    assert result.language == "en"


def test_language_registry():
    from translation.language_registry import all_language_options, get_display_name
    opts = all_language_options()
    assert len(opts) >= 10
    assert get_display_name("en") == "English"
    assert get_display_name("ta") == "Tamil"


def test_translation_cache():
    from translation.translation_cache import TranslationCache
    cache = TranslationCache(maxsize=5)
    cache.set("hello", "ta", "வணக்கம்")
    assert cache.get("hello", "ta") == "வணக்கம்"
    assert cache.get("hello", "hi") is None


# ── Agents ────────────────────────────────────────────────────────────────────
def test_appointment_agent_kwargs():
    """Ensure AppointmentAgent accepts language, model, database kwargs."""
    from agents.appointment_agent import AppointmentAgent
    # Must not raise TypeError
    agent = AppointmentAgent(language="ta", model="qwen3", database=None)
    assert agent.language == "ta"


def test_appointment_agent_greet():
    from agents.appointment_agent import AppointmentAgent
    agent = AppointmentAgent(user_id=1, language="en")
    resp  = agent.process("start")
    assert resp.message != ""
    assert "name" in resp.message.lower()


def test_appointment_agent_emergency():
    from agents.appointment_agent import AppointmentAgent
    agent = AppointmentAgent()
    resp  = agent.process("I have severe chest pain and can't breathe")
    assert resp.emergency is True
    assert "108" in resp.message or "emergency" in resp.message.lower()


def test_prescription_agent_no_image():
    from agents.prescription_agent import PrescriptionAgent
    agent = PrescriptionAgent(user_id=1)
    resp  = agent.process("hello")
    assert "image" in resp.message.lower()


def test_reminder_agent_invalid_time():
    from agents.reminder_agent import ReminderAgent
    agent = ReminderAgent(user_id=1)
    resp  = agent.create("not-a-time")
    assert resp.success is False


# ── Appointment service ───────────────────────────────────────────────────────
def test_find_specialist():
    from appointment.doctor_registry import find_specialist
    result = find_specialist("I have chest pain and shortness of breath")
    assert result["specialty"] == "Cardiologist"
    assert len(result["doctors"]) > 0


def test_get_available_slots():
    from appointment.doctor_registry import get_available_slots
    slots = get_available_slots("Dr. Test")
    assert len(slots) > 0


# ── Schemas ───────────────────────────────────────────────────────────────────
def test_user_register_schema():
    from utils.schemas import UserRegisterSchema
    schema = UserRegisterSchema(
        username="john_doe", password="secret123",
        full_name="John Doe", age=65,
    )
    assert schema.username == "john_doe"


def test_user_register_schema_invalid():
    from utils.schemas import UserRegisterSchema
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        UserRegisterSchema(username="ab", password="x", full_name="J")


def test_appointment_schema_past_date():
    from utils.schemas import AppointmentCreateSchema
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        AppointmentCreateSchema(
            doctor_name="Dr. Test",
            apt_date=date(2000, 1, 1),
            apt_time="09:00 AM",
        )


# ═════════════════════════════════════════════════════════════════════════════
# Infrastructure tests (added by infrastructure upgrade)
# ═════════════════════════════════════════════════════════════════════════════

# ── ConfigManager ─────────────────────────────────────────────────────────────
def test_config_manager_singleton():
    from config import get_config, ConfigManager
    cfg1 = get_config()
    cfg2 = get_config()
    assert cfg1 is cfg2
    assert isinstance(cfg1, ConfigManager)


def test_config_manager_properties():
    from config import get_config
    cfg = get_config()
    assert cfg.BASE_DIR.exists()
    assert cfg.LOG_DIR.exists()
    assert cfg.DATA_DIR.exists()
    assert cfg.UPLOAD_DIR.exists()
    assert cfg.DATABASE_URL.startswith("sqlite:///")
    assert cfg.APP_ENV in ("development", "staging", "production")
    assert 0.0 <= cfg.LLM_TEMPERATURE <= 2.0
    assert 256 <= cfg.LLM_MAX_TOKENS <= 8192
    assert cfg.WHISPER_MODEL in ("tiny", "base", "small", "medium", "large")


def test_config_manager_backward_compat():
    """All existing module-level constants must still be importable."""
    from config import (
        BASE_DIR, DB_PATH, LOG_DIR, DATABASE_URL, DB_ECHO,
        OLLAMA_BASE_URL, LLM_MODELS, LLM_MAX_TOKENS, LLM_TEMPERATURE,
        OCR_CONFIDENCE_THRESHOLD, OCR_FALLBACK_THRESHOLD,
        DEFAULT_LANGUAGE, WHISPER_MODEL, REMINDER_SNOOZE_MINUTES,
        APP_TITLE, APP_ICON, LOG_LEVEL, LOG_MAX_BYTES,
    )
    assert isinstance(BASE_DIR, Path)
    assert isinstance(LLM_MODELS, list)
    assert len(LLM_MODELS) >= 1
    assert isinstance(LLM_TEMPERATURE, float)


def test_config_validate():
    from config import get_config
    warnings = get_config().validate()
    assert isinstance(warnings, list)


def test_config_as_dict():
    from config import get_config
    d = get_config().as_dict()
    assert "APP_ENV" in d
    assert "LLM_MODELS" in d
    assert "APP_SECRET_KEY" not in d   # secret must not appear


def test_config_feature_flags():
    from config import get_config
    cfg = get_config()
    assert isinstance(cfg.FEATURE_VOICE, bool)
    assert isinstance(cfg.FEATURE_OCR, bool)
    assert isinstance(cfg.FEATURE_REMINDERS, bool)
    assert isinstance(cfg.FEATURE_APPOINTMENTS, bool)
    assert isinstance(cfg.FEATURE_TRANSLATION, bool)


# ── LogManager ────────────────────────────────────────────────────────────────
def test_log_manager_singleton():
    from utils.logger import get_log_manager
    lm1 = get_log_manager()
    lm2 = get_log_manager()
    assert lm1 is lm2


def test_log_manager_get_logger():
    from utils.logger import get_log_manager
    lm = get_log_manager()
    log1 = lm.get_logger("test.module.a")
    log2 = lm.get_logger("test.module.a")
    assert log1 is log2   # idempotent


def test_log_manager_context():
    from utils.logger import get_log_manager
    lm = get_log_manager()
    lm.set_context(request_id="abc-123", user_id=42)
    ctx = lm.get_context()
    assert ctx["request_id"] == "abc-123"
    assert ctx["user_id"] == 42
    lm.clear_context()
    assert lm.get_context() == {}


def test_log_manager_backward_compat():
    """get_logger(__name__) must still work."""
    from utils.logger import get_logger
    import logging
    log = get_logger("test.backward.compat")
    assert isinstance(log, logging.Logger)


# ── GlobalExceptionHandler ────────────────────────────────────────────────────
def test_exception_handler_singleton():
    from utils.error_handler import get_exception_handler
    h1 = get_exception_handler()
    h2 = get_exception_handler()
    assert h1 is h2


def test_exception_handler_classify_db():
    from utils.error_handler import get_exception_handler, ErrorCode
    h = get_exception_handler()
    err = h.handle(Exception("OperationalError: database is locked"), log_tb=False)
    assert err.code == ErrorCode.DB_CONNECTION
    assert err.recoverable is False


def test_exception_handler_classify_llm():
    from utils.error_handler import get_exception_handler, ErrorCode
    h = get_exception_handler()
    err = h.handle(Exception("Connection refused to ollama"), log_tb=False)
    assert err.code == ErrorCode.LLM_UNAVAILABLE
    assert err.recoverable is True


def test_exception_handler_classify_timeout():
    from utils.error_handler import get_exception_handler, ErrorCode
    h = get_exception_handler()
    err = h.handle(Exception("Read timeout after 120s"), log_tb=False)
    assert err.code == ErrorCode.LLM_TIMEOUT


def test_exception_handler_classify_unknown():
    from utils.error_handler import get_exception_handler, ErrorCode
    h = get_exception_handler()
    err = h.handle(Exception("something completely unexpected"), log_tb=False)
    assert err.code == ErrorCode.UNKNOWN
    assert err.recoverable is True


def test_exception_handler_passthrough_app_error():
    from utils.error_handler import get_exception_handler, AppError, ErrorCode
    h = get_exception_handler()
    original = AppError("custom error", code=ErrorCode.VALIDATION)
    result = h.handle(original, log_tb=False)
    assert result is original


def test_safe_execute_backward_compat():
    from utils.error_handler import safe_execute

    @safe_execute(fallback="default")
    def boom():
        raise RuntimeError("test error")

    assert boom() == "default"


def test_safe_execute_dict_fallback_has_error_code():
    from utils.error_handler import safe_execute

    @safe_execute(fallback={})
    def boom():
        raise Exception("OperationalError: database is locked")

    result = boom()
    assert "error" in result
    assert "error_code" in result
    assert result["error_code"] == "DB_001"


def test_format_user_error_backward_compat():
    from utils.error_handler import format_user_error
    msg = format_user_error(Exception("Connection refused to ollama"))
    assert isinstance(msg, str)
    assert len(msg) > 0


# ── DatabaseManager ───────────────────────────────────────────────────────────
def test_db_manager_singleton():
    from database.engine import get_db_manager
    dm1 = get_db_manager()
    dm2 = get_db_manager()
    assert dm1 is dm2


def test_db_manager_health_check():
    from database.engine import get_db_manager
    dm = get_db_manager()
    dm.init_db()
    assert dm.health_check() is True


def test_db_manager_stats():
    from database.engine import get_db_manager
    dm = get_db_manager()
    stats = dm.stats()
    assert "healthy" in stats
    assert "sessions_opened" in stats
    assert "sessions_active" in stats
    assert stats["healthy"] is True


def test_db_manager_session_counts():
    from database.engine import get_db_manager
    dm = get_db_manager()
    before = dm.stats()["sessions_opened"]
    with dm.session() as s:
        assert s is not None
    after = dm.stats()["sessions_opened"]
    assert after == before + 1


def test_get_session_backward_compat():
    """with get_session() as session: must still work."""
    from database.engine import get_session
    with get_session() as session:
        assert session is not None


def test_init_db_backward_compat():
    from database.engine import init_db
    init_db()   # must not raise


# ── DI Container ─────────────────────────────────────────────────────────────
def test_container_singleton():
    from core.container import container, _Container
    assert isinstance(container, _Container)


def test_container_config():
    from core.container import container
    from config import ConfigManager
    cfg = container.config()
    assert isinstance(cfg, ConfigManager)


def test_container_log_manager():
    from core.container import container
    from utils.logger import LogManager
    lm = container.log_manager()
    assert isinstance(lm, LogManager)


def test_container_logger():
    import logging
    from core.container import container
    log = container.logger("test.container.logger")
    assert isinstance(log, logging.Logger)


def test_container_exception_handler():
    from core.container import container
    from utils.error_handler import GlobalExceptionHandler
    h = container.exception_handler()
    assert isinstance(h, GlobalExceptionHandler)


def test_container_db_manager():
    from core.container import container
    from database.engine import DatabaseManager
    dm = container.db_manager()
    assert isinstance(dm, DatabaseManager)


def test_container_bootstrap_idempotent():
    from core.container import container
    container.bootstrap()
    container.bootstrap()   # second call must be a no-op, not raise


def test_container_health():
    from core.container import container
    container.bootstrap()
    h = container.health()
    assert "app_env" in h
    assert "database" in h
    assert "llm" in h
    assert "features" in h
    assert h["database"]["healthy"] is True


# ── Cross-cutting: agents still use infrastructure ────────────────────────────
def test_agents_use_shared_logger():
    """Verify agents import get_logger from utils.logger (not a local copy)."""
    import importlib, inspect
    for mod_name in [
        "agents.prescription_agent",
        "agents.appointment_agent",
        "agents.conversation_agent",
        "agents.reminder_agent",
    ]:
        mod = importlib.import_module(mod_name)
        src = inspect.getsource(mod)
        assert "from utils.logger import get_logger" in src, (
            f"{mod_name} does not use shared get_logger"
        )


def test_agents_use_shared_error_handler():
    """Verify prescription_agent uses safe_execute from utils.error_handler."""
    import importlib, inspect
    mod = importlib.import_module("agents.prescription_agent")
    src = inspect.getsource(mod)
    assert "from utils.error_handler import safe_execute" in src


def test_services_use_shared_get_session():
    """Verify reminder_service uses get_session from database.engine."""
    import importlib, inspect
    mod = importlib.import_module("reminder.reminder_service")
    src = inspect.getsource(mod)
    assert "from database.engine import get_session" in src
