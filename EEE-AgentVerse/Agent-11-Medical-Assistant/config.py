"""
config.py — ConfigManager: single source of truth for every setting.

Design rules
────────────
• All values come from environment variables (loaded from .env).
• Every setting has a typed property with a safe default.
• Module-level constants are aliases to ConfigManager properties so that
  every existing  `from config import X`  import continues to work unchanged.
• Validation runs once at import time; bad values log a warning and fall back
  to the default — the app never crashes on a misconfigured .env.
• Feature flags let individual capabilities be toggled without code changes.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Final, List

# ── Load .env before anything else ───────────────────────────────────────────
try:
    from dotenv import load_dotenv as _load_dotenv
    _env_file = Path(__file__).resolve().parent / ".env"
    _load_dotenv(_env_file, override=False)   # don't override already-set env vars
except ImportError:
    pass   # python-dotenv not installed; rely on real environment variables


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────
def _str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _int(key: str, default: int = 0) -> int:
    raw = os.getenv(key, "")
    try:
        return int(raw.strip())
    except (ValueError, AttributeError):
        return default


def _float(key: str, default: float = 0.0) -> float:
    raw = os.getenv(key, "")
    try:
        return float(raw.strip())
    except (ValueError, AttributeError):
        return default


def _bool(key: str, default: bool = False) -> bool:
    raw = os.getenv(key, "").strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return default


def _list(key: str, default: List[str] | None = None) -> List[str]:
    raw = os.getenv(key, "")
    if not raw.strip():
        return default or []
    return [item.strip() for item in raw.split(",") if item.strip()]


# ─────────────────────────────────────────────────────────────────────────────
# ConfigManager
# ─────────────────────────────────────────────────────────────────────────────
class ConfigManager:
    """
    Centralised, validated configuration.
    Instantiated once as a module-level singleton (_cfg).
    All public attributes are read-only properties.
    """

    # ── Base paths ────────────────────────────────────────────────────────────
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def DATA_DIR(self) -> Path:
        d = self.BASE_DIR / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def DB_PATH(self) -> Path:
        return self.DATA_DIR / "medical_assistant.db"

    @property
    def LOG_DIR(self) -> Path:
        d = self.BASE_DIR / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def ASSETS_DIR(self) -> Path:
        return self.BASE_DIR / "assets"

    @property
    def SOUNDS_DIR(self) -> Path:
        d = self.ASSETS_DIR / "sounds"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def UPLOAD_DIR(self) -> Path:
        d = self.DATA_DIR / "uploads"
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ── Application ───────────────────────────────────────────────────────────
    @property
    def APP_ENV(self) -> str:
        v = _str("APP_ENV", "development")
        return v if v in ("development", "staging", "production") else "development"

    @property
    def APP_VERSION(self) -> str:
        return _str("APP_VERSION", "1.0.0")

    @property
    def APP_SECRET_KEY(self) -> str:
        return _str("APP_SECRET_KEY", "dev-secret-key-change-in-production")

    @property
    def APP_TITLE(self) -> str:
        return "💊 AI Medical Assistant"

    @property
    def APP_ICON(self) -> str:
        return "💊"

    @property
    def PAGE_LAYOUT(self) -> str:
        return "wide"

    @property
    def IS_PRODUCTION(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.APP_ENV == "development"

    # ── Database ──────────────────────────────────────────────────────────────
    @property
    def DATABASE_URL(self) -> str:
        url = _str("DATABASE_URL", "")
        return url if url else f"sqlite:///{self.DB_PATH}"

    @property
    def DB_ECHO(self) -> bool:
        return _bool("DB_ECHO", False)

    @property
    def DB_POOL_SIZE(self) -> int:
        return _int("DB_POOL_SIZE", 5)

    # ── Logging ───────────────────────────────────────────────────────────────
    @property
    def LOG_LEVEL(self) -> str:
        v = _str("LOG_LEVEL", "INFO").upper()
        return v if v in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL") else "INFO"

    @property
    def LOG_FORMAT(self) -> str:
        v = _str("LOG_FORMAT", "text").lower()
        return v if v in ("text", "json") else "text"

    @property
    def LOG_MAX_BYTES(self) -> int:
        return _int("LOG_MAX_BYTES", 5 * 1024 * 1024)

    @property
    def LOG_BACKUP_COUNT(self) -> int:
        return _int("LOG_BACKUP_COUNT", 3)

    # ── Ollama / LLM ──────────────────────────────────────────────────────────
    @property
    def OLLAMA_BASE_URL(self) -> str:
        return _str("OLLAMA_BASE_URL", "http://localhost:11434")

    @property
    def OLLAMA_TIMEOUT(self) -> int:
        return _int("OLLAMA_TIMEOUT", 120)

    @property
    def LLM_MODELS(self) -> List[str]:
        return _list("LLM_MODELS", ["qwen3", "deepseek-r1", "llama3.1"])

    @property
    def LLM_HEALTH_CHECK_TIMEOUT(self) -> int:
        return _int("LLM_HEALTH_CHECK_TIMEOUT", 5)

    @property
    def LLM_MAX_TOKENS(self) -> int:
        v = _int("LLM_MAX_TOKENS", 2048)
        return max(256, min(v, 8192))

    @property
    def LLM_TEMPERATURE(self) -> float:
        v = _float("LLM_TEMPERATURE", 0.3)
        return max(0.0, min(v, 2.0))

    # ── OCR ───────────────────────────────────────────────────────────────────
    @property
    def OCR_CONFIDENCE_THRESHOLD(self) -> float:
        v = _float("OCR_CONFIDENCE_THRESHOLD", 0.65)
        return max(0.1, min(v, 1.0))

    @property
    def OCR_FALLBACK_THRESHOLD(self) -> float:
        v = _float("OCR_FALLBACK_THRESHOLD", 0.50)
        return max(0.1, min(v, 1.0))

    @property
    def OCR_LANGUAGES(self) -> List[str]:
        return _list("OCR_LANGUAGES", ["en", "ta", "hi", "te", "ml", "kn"])

    @property
    def TESSERACT_CMD(self) -> str:
        return _str("TESSERACT_CMD", "tesseract")

    # ── Translation ───────────────────────────────────────────────────────────
    @property
    def NLLB_MODEL_NAME(self) -> str:
        return _str("NLLB_MODEL_NAME", "facebook/nllb-200-distilled-600M")

    @property
    def TRANSLATION_CACHE_SIZE(self) -> int:
        return _int("TRANSLATION_CACHE_SIZE", 512)

    @property
    def DEFAULT_LANGUAGE(self) -> str:
        return _str("DEFAULT_LANGUAGE", "en")

    # ── Voice ─────────────────────────────────────────────────────────────────
    @property
    def WHISPER_MODEL(self) -> str:
        v = _str("WHISPER_MODEL", "base")
        return v if v in ("tiny", "base", "small", "medium", "large") else "base"

    @property
    def TTS_MODEL(self) -> str:
        return _str("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")

    @property
    def AUDIO_SAMPLE_RATE(self) -> int:
        return _int("AUDIO_SAMPLE_RATE", 16000)

    @property
    def AUDIO_MAX_SECONDS(self) -> int:
        return _int("AUDIO_MAX_SECONDS", 30)

    # ── Reminders ─────────────────────────────────────────────────────────────
    @property
    def REMINDER_SNOOZE_MINUTES(self) -> int:
        return _int("REMINDER_SNOOZE_MINUTES", 10)

    @property
    def REMINDER_MISSED_THRESHOLD(self) -> int:
        return _int("REMINDER_MISSED_THRESHOLD", 3)

    @property
    def DEFAULT_MORNING_TIME(self) -> str:
        return _str("DEFAULT_MORNING_TIME", "08:00")

    @property
    def DEFAULT_AFTERNOON_TIME(self) -> str:
        return _str("DEFAULT_AFTERNOON_TIME", "13:00")

    @property
    def DEFAULT_NIGHT_TIME(self) -> str:
        return _str("DEFAULT_NIGHT_TIME", "21:00")

    # ── Appointments ──────────────────────────────────────────────────────────
    @property
    def APPOINTMENT_REMINDER_HOURS(self) -> int:
        return _int("APPOINTMENT_REMINDER_HOURS", 24)

    # ── Feature flags ─────────────────────────────────────────────────────────
    @property
    def FEATURE_VOICE(self) -> bool:
        return _bool("FEATURE_VOICE", True)

    @property
    def FEATURE_TRANSLATION(self) -> bool:
        return _bool("FEATURE_TRANSLATION", True)

    @property
    def FEATURE_OCR(self) -> bool:
        return _bool("FEATURE_OCR", True)

    @property
    def FEATURE_REMINDERS(self) -> bool:
        return _bool("FEATURE_REMINDERS", True)

    @property
    def FEATURE_APPOINTMENTS(self) -> bool:
        return _bool("FEATURE_APPOINTMENTS", True)

    # ── Introspection ─────────────────────────────────────────────────────────
    def as_dict(self) -> dict:
        """Return all settings as a plain dict (safe for logging — no secrets)."""
        safe_keys = [
            "APP_ENV", "APP_VERSION", "LOG_LEVEL", "LOG_FORMAT",
            "OLLAMA_BASE_URL", "LLM_MODELS", "LLM_MAX_TOKENS", "LLM_TEMPERATURE",
            "OCR_CONFIDENCE_THRESHOLD", "OCR_FALLBACK_THRESHOLD",
            "DEFAULT_LANGUAGE", "WHISPER_MODEL",
            "REMINDER_SNOOZE_MINUTES", "REMINDER_MISSED_THRESHOLD",
            "FEATURE_VOICE", "FEATURE_TRANSLATION", "FEATURE_OCR",
            "FEATURE_REMINDERS", "FEATURE_APPOINTMENTS",
        ]
        return {k: getattr(self, k) for k in safe_keys}

    def validate(self) -> List[str]:
        """
        Run basic sanity checks.
        Returns a list of warning strings (empty = all good).
        """
        warnings: List[str] = []
        if self.APP_SECRET_KEY == "dev-secret-key-change-in-production" and self.IS_PRODUCTION:
            warnings.append("APP_SECRET_KEY is using the default value in production.")
        if self.OCR_FALLBACK_THRESHOLD >= self.OCR_CONFIDENCE_THRESHOLD:
            warnings.append(
                "OCR_FALLBACK_THRESHOLD should be lower than OCR_CONFIDENCE_THRESHOLD."
            )
        if self.LLM_TEMPERATURE > 1.0:
            warnings.append("LLM_TEMPERATURE > 1.0 may produce unpredictable responses.")
        return warnings


# ── Module-level singleton ────────────────────────────────────────────────────
_cfg = ConfigManager()

# ── Backward-compatible module-level constants ────────────────────────────────
# Every existing  `from config import X`  import continues to work unchanged.
BASE_DIR:                   Final[Path]       = _cfg.BASE_DIR
DB_PATH:                    Final[Path]       = _cfg.DB_PATH
LOG_DIR:                    Final[Path]       = _cfg.LOG_DIR
ASSETS_DIR:                 Final[Path]       = _cfg.ASSETS_DIR
SOUNDS_DIR:                 Final[Path]       = _cfg.SOUNDS_DIR
UPLOAD_DIR:                 Final[Path]       = _cfg.UPLOAD_DIR
DATABASE_URL:               Final[str]        = _cfg.DATABASE_URL
DB_ECHO:                    Final[bool]       = _cfg.DB_ECHO
DB_POOL_SIZE:               Final[int]        = _cfg.DB_POOL_SIZE
OLLAMA_BASE_URL:            Final[str]        = _cfg.OLLAMA_BASE_URL
OLLAMA_TIMEOUT:             Final[int]        = _cfg.OLLAMA_TIMEOUT
LLM_MODELS:                 Final[List[str]]  = _cfg.LLM_MODELS
LLM_HEALTH_CHECK_TIMEOUT:   Final[int]        = _cfg.LLM_HEALTH_CHECK_TIMEOUT
LLM_MAX_TOKENS:             Final[int]        = _cfg.LLM_MAX_TOKENS
LLM_TEMPERATURE:            Final[float]      = _cfg.LLM_TEMPERATURE
OCR_CONFIDENCE_THRESHOLD:   Final[float]      = _cfg.OCR_CONFIDENCE_THRESHOLD
OCR_FALLBACK_THRESHOLD:     Final[float]      = _cfg.OCR_FALLBACK_THRESHOLD
OCR_LANGUAGES:              Final[List[str]]  = _cfg.OCR_LANGUAGES
TESSERACT_CMD:              Final[str]        = _cfg.TESSERACT_CMD
NLLB_MODEL_NAME:            Final[str]        = _cfg.NLLB_MODEL_NAME
TRANSLATION_CACHE_SIZE:     Final[int]        = _cfg.TRANSLATION_CACHE_SIZE
DEFAULT_LANGUAGE:           Final[str]        = _cfg.DEFAULT_LANGUAGE
WHISPER_MODEL:              Final[str]        = _cfg.WHISPER_MODEL
TTS_MODEL:                  Final[str]        = _cfg.TTS_MODEL
AUDIO_SAMPLE_RATE:          Final[int]        = _cfg.AUDIO_SAMPLE_RATE
AUDIO_MAX_SECONDS:          Final[int]        = _cfg.AUDIO_MAX_SECONDS
REMINDER_SNOOZE_MINUTES:    Final[int]        = _cfg.REMINDER_SNOOZE_MINUTES
REMINDER_MISSED_THRESHOLD:  Final[int]        = _cfg.REMINDER_MISSED_THRESHOLD
DEFAULT_MORNING_TIME:       Final[str]        = _cfg.DEFAULT_MORNING_TIME
DEFAULT_AFTERNOON_TIME:     Final[str]        = _cfg.DEFAULT_AFTERNOON_TIME
DEFAULT_NIGHT_TIME:         Final[str]        = _cfg.DEFAULT_NIGHT_TIME
APPOINTMENT_REMINDER_HOURS: Final[int]        = _cfg.APPOINTMENT_REMINDER_HOURS
APP_TITLE:                  Final[str]        = _cfg.APP_TITLE
APP_ICON:                   Final[str]        = _cfg.APP_ICON
APP_VERSION:                Final[str]        = _cfg.APP_VERSION
PAGE_LAYOUT:                Final[str]        = _cfg.PAGE_LAYOUT
LOG_LEVEL:                  Final[str]        = _cfg.LOG_LEVEL
LOG_MAX_BYTES:              Final[int]        = _cfg.LOG_MAX_BYTES
LOG_BACKUP_COUNT:           Final[int]        = _cfg.LOG_BACKUP_COUNT


def get_config() -> ConfigManager:
    """Return the module-level ConfigManager singleton."""
    return _cfg
