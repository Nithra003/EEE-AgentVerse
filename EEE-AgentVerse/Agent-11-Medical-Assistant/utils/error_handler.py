"""
utils/error_handler.py — GlobalExceptionHandler + @safe_execute decorator.

Backward compatibility
──────────────────────
  safe_execute(...)        ← still works everywhere, unchanged.
  format_user_error(exc)   ← still works everywhere, unchanged.

New capabilities
────────────────
  • AppError typed exception hierarchy with error codes
  • GlobalExceptionHandler.handle() — categorises, logs, returns AppError
  • GlobalExceptionHandler.display() — renders user-friendly Streamlit UI
  • @safe_execute now attaches error_code to dict fallbacks
"""
from __future__ import annotations

import functools
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from utils.logger import get_logger

log = get_logger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


# ─────────────────────────────────────────────────────────────────────────────
# Error taxonomy
# ─────────────────────────────────────────────────────────────────────────────
class ErrorCode(str, Enum):
    # Infrastructure
    DB_CONNECTION      = "DB_001"
    DB_QUERY           = "DB_002"
    DB_INTEGRITY       = "DB_003"
    # AI / LLM
    LLM_UNAVAILABLE    = "AI_001"
    LLM_TIMEOUT        = "AI_002"
    LLM_PARSE          = "AI_003"
    # OCR
    OCR_LOW_CONFIDENCE = "OCR_001"
    OCR_ENGINE_FAIL    = "OCR_002"
    OCR_IMAGE_INVALID  = "OCR_003"
    # Voice
    STT_UNAVAILABLE    = "VOI_001"
    TTS_UNAVAILABLE    = "VOI_002"
    # Translation
    TRANSLATION_FAIL   = "TRN_001"
    # Validation
    VALIDATION         = "VAL_001"
    # Generic
    UNKNOWN            = "GEN_001"
    NOT_FOUND          = "GEN_002"
    PERMISSION_DENIED  = "GEN_003"


@dataclass
class AppError(Exception):
    """Typed application error with user-facing message and error code."""
    message:    str
    code:       ErrorCode = ErrorCode.UNKNOWN
    detail:     str       = ""
    recoverable: bool     = True

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# ─────────────────────────────────────────────────────────────────────────────
# GlobalExceptionHandler
# ─────────────────────────────────────────────────────────────────────────────
class GlobalExceptionHandler:
    """
    Centralised exception handler.
    • Categorises raw exceptions into AppError with the right ErrorCode.
    • Logs with full traceback at ERROR level.
    • Returns a structured AppError — never re-raises.
    • Provides a Streamlit display helper.
    """

    # ── Classification map: substring → (ErrorCode, user message, recoverable) ──
    _RULES: list[tuple[list[str], ErrorCode, str, bool]] = [
        (
            ["operationalerror", "no such table", "database is locked"],
            ErrorCode.DB_CONNECTION,
            "Database connection error. Please restart the application.",
            False,
        ),
        (
            ["integrityerror", "unique constraint", "foreign key"],
            ErrorCode.DB_INTEGRITY,
            "A data conflict occurred. The record may already exist.",
            True,
        ),
        (
            ["connection refused", "connection error", "ollama"],
            ErrorCode.LLM_UNAVAILABLE,
            "AI service is unavailable. Please ensure Ollama is running.",
            True,
        ),
        (
            ["timeout", "timed out", "read timeout"],
            ErrorCode.LLM_TIMEOUT,
            "The request timed out. Please try again.",
            True,
        ),
        (
            ["json", "parse", "decode"],
            ErrorCode.LLM_PARSE,
            "Could not parse the AI response. Please try again.",
            True,
        ),
        (
            ["easyocr", "tesseract", "ocr"],
            ErrorCode.OCR_ENGINE_FAIL,
            "OCR engine failed. Please upload a clearer image.",
            True,
        ),
        (
            ["whisper", "speech", "audio"],
            ErrorCode.STT_UNAVAILABLE,
            "Voice recognition is unavailable. Please type your input.",
            True,
        ),
        (
            ["tts", "coqui", "synthesis"],
            ErrorCode.TTS_UNAVAILABLE,
            "Text-to-speech is unavailable. Browser voice will be used.",
            True,
        ),
        (
            ["translation", "nllb", "flores"],
            ErrorCode.TRANSLATION_FAIL,
            "Translation failed. Showing content in English.",
            True,
        ),
        (
            ["validationerror", "validation error"],
            ErrorCode.VALIDATION,
            "Invalid input. Please check your entries and try again.",
            True,
        ),
        (
            ["not found", "404", "no result"],
            ErrorCode.NOT_FOUND,
            "The requested item was not found.",
            True,
        ),
        (
            ["permission", "access denied", "unauthorized"],
            ErrorCode.PERMISSION_DENIED,
            "You do not have permission to perform this action.",
            False,
        ),
        (
            ["memory", "oom", "out of memory"],
            ErrorCode.UNKNOWN,
            "Not enough memory. Please close other applications and retry.",
            False,
        ),
    ]

    def handle(
        self,
        exc: Exception,
        context: str = "",
        log_tb: bool = True,
    ) -> AppError:
        """
        Classify `exc`, log it, and return a structured AppError.
        Never re-raises.
        """
        if isinstance(exc, AppError):
            log.error("AppError [%s] in %s: %s", exc.code, context, exc.message)
            return exc

        exc_str = f"{type(exc).__name__}: {exc}".lower()
        tb_str  = traceback.format_exc()

        if log_tb:
            log.error("Exception in %s:\n%s", context or "unknown", tb_str)
        else:
            log.error("Exception in %s: %s", context or "unknown", exc)

        for keywords, code, user_msg, recoverable in self._RULES:
            if any(kw in exc_str for kw in keywords):
                return AppError(
                    message=user_msg,
                    code=code,
                    detail=str(exc),
                    recoverable=recoverable,
                )

        return AppError(
            message="An unexpected error occurred. Please try again.",
            code=ErrorCode.UNKNOWN,
            detail=str(exc),
            recoverable=True,
        )

    def display(self, error: AppError) -> None:
        """
        Render a user-friendly error in Streamlit.
        Gracefully degrades if Streamlit is not available.
        """
        try:
            import streamlit as st
            icon = "⚠️" if error.recoverable else "🚨"
            if error.recoverable:
                st.warning(f"{icon} {error.message}")
            else:
                st.error(f"{icon} {error.message}")
            if not error.recoverable:
                st.info("Please restart the application or contact support.")
        except Exception:
            print(f"ERROR [{error.code}]: {error.message}")

    def display_raw(self, exc: Exception, context: str = "") -> None:
        """Classify, log, and display in one call."""
        app_error = self.handle(exc, context)
        self.display(app_error)


# ── Module-level singleton ────────────────────────────────────────────────────
_handler = GlobalExceptionHandler()


def get_exception_handler() -> GlobalExceptionHandler:
    """Return the module-level GlobalExceptionHandler singleton."""
    return _handler


# ─────────────────────────────────────────────────────────────────────────────
# @safe_execute decorator — fully backward-compatible
# ─────────────────────────────────────────────────────────────────────────────
def safe_execute(
    fallback: Any = None,
    user_message: str = "Something went wrong. Please try again.",
    log_tb: bool = True,
) -> Callable[[F], F]:
    """
    Decorator factory.
    Catches all exceptions, logs them via GlobalExceptionHandler,
    and returns `fallback` instead of re-raising.

    Backward-compatible: existing usage is unchanged.
    Enhancement: dict fallbacks now include 'error_code' field.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                app_error = _handler.handle(exc, context=func.__qualname__, log_tb=log_tb)
                if isinstance(fallback, dict):
                    result = dict(fallback)
                    result.setdefault("error", user_message)
                    result.setdefault("error_code", app_error.code.value)
                    return result
                return fallback
        return wrapper  # type: ignore[return-value]
    return decorator


# ── Backward-compatible helper ────────────────────────────────────────────────
def format_user_error(exc: Exception) -> str:
    """
    Backward-compatible function.
    Every existing  `format_user_error(exc)`  call works unchanged.
    """
    return _handler.handle(exc).message
