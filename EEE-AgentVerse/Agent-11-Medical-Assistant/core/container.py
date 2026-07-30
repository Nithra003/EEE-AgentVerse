"""
core/container.py — Dependency Injection container.

Responsibilities
────────────────
• Single registry for every shared service/manager.
• Lazy initialisation — services are created on first access.
• Thread-safe singleton per service.
• Provides typed accessors so callers never import concrete classes directly.
• bootstrap() wires everything together and validates the environment.

Usage
─────
    from core.container import container

    router = container.llm_router()
    db     = container.db_manager()
    cfg    = container.config()
    log    = container.logger("my.module")
"""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import logging
    from config import ConfigManager
    from database.engine import DatabaseManager
    from ai.llm_router import LLMRouter
    from utils.logger import LogManager
    from utils.error_handler import GlobalExceptionHandler


class _Container:
    """
    Lazy-initialising DI container.
    All service factories are called at most once (double-checked locking).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Slots for each singleton
        self._config:            Optional["ConfigManager"]         = None
        self._log_manager:       Optional["LogManager"]            = None
        self._db_manager:        Optional["DatabaseManager"]       = None
        self._llm_router:        Optional["LLMRouter"]             = None
        self._exception_handler: Optional["GlobalExceptionHandler"] = None
        self._bootstrapped:      bool                              = False

    # ── Config ────────────────────────────────────────────────────────────────
    def config(self) -> "ConfigManager":
        if self._config is None:
            with self._lock:
                if self._config is None:
                    from config import get_config
                    self._config = get_config()
        return self._config

    # ── Logger ────────────────────────────────────────────────────────────────
    def log_manager(self) -> "LogManager":
        if self._log_manager is None:
            with self._lock:
                if self._log_manager is None:
                    from utils.logger import get_log_manager
                    self._log_manager = get_log_manager()
        return self._log_manager

    def logger(self, name: str) -> "logging.Logger":
        """Convenience: get a named logger without importing utils.logger."""
        return self.log_manager().get_logger(name)

    # ── Exception handler ─────────────────────────────────────────────────────
    def exception_handler(self) -> "GlobalExceptionHandler":
        if self._exception_handler is None:
            with self._lock:
                if self._exception_handler is None:
                    from utils.error_handler import get_exception_handler
                    self._exception_handler = get_exception_handler()
        return self._exception_handler

    # ── Database ──────────────────────────────────────────────────────────────
    def db_manager(self) -> "DatabaseManager":
        if self._db_manager is None:
            with self._lock:
                if self._db_manager is None:
                    from database.engine import get_db_manager
                    self._db_manager = get_db_manager()
        return self._db_manager

    # ── LLM Router ────────────────────────────────────────────────────────────
    def llm_router(self) -> "LLMRouter":
        if self._llm_router is None:
            with self._lock:
                if self._llm_router is None:
                    from ai.llm_router import get_router
                    self._llm_router = get_router()
        return self._llm_router

    # ── Bootstrap ─────────────────────────────────────────────────────────────
    def bootstrap(self) -> None:
        """
        Wire all services, validate config, initialise DB schema.
        Call once at application startup (app.py).
        Safe to call multiple times — subsequent calls are no-ops.
        """
        if self._bootstrapped:
            return

        with self._lock:
            if self._bootstrapped:
                return

            log = self.logger("core.container")
            cfg = self.config()

            # ── Validate config ───────────────────────────────────────────────
            warnings = cfg.validate()
            for w in warnings:
                log.warning("Config warning: %s", w)

            log.info(
                "Bootstrap | env=%s version=%s log_level=%s",
                cfg.APP_ENV, cfg.APP_VERSION, cfg.LOG_LEVEL,
            )

            # ── Initialise database ───────────────────────────────────────────
            try:
                db = self.db_manager()
                db.init_db()
                if db.health_check():
                    log.info("Database: healthy ✓")
                else:
                    log.error("Database: health check FAILED")
            except Exception as exc:
                self.exception_handler().handle(exc, context="bootstrap.db")

            # ── Log LLM availability ──────────────────────────────────────────
            try:
                router = self.llm_router()
                log.info(
                    "LLM Router: active_model=%s available=%s",
                    router.active_model_name,
                    router.is_any_available(),
                )
            except Exception as exc:
                self.exception_handler().handle(exc, context="bootstrap.llm")

            # ── Log feature flags ─────────────────────────────────────────────
            flags = {
                "voice":        cfg.FEATURE_VOICE,
                "translation":  cfg.FEATURE_TRANSLATION,
                "ocr":          cfg.FEATURE_OCR,
                "reminders":    cfg.FEATURE_REMINDERS,
                "appointments": cfg.FEATURE_APPOINTMENTS,
            }
            log.info("Feature flags: %s", flags)

            self._bootstrapped = True
            log.info("Bootstrap complete ✓")

    # ── Health summary ────────────────────────────────────────────────────────
    def health(self) -> dict:
        """Return a health summary dict for the Settings / Status page."""
        cfg = self.config()
        try:
            db_stats = self.db_manager().stats()
        except Exception:
            db_stats = {"healthy": False}

        try:
            router = self.llm_router()
            llm_ok = router.is_any_available()
            llm_model = router.active_model_name
        except Exception:
            llm_ok    = False
            llm_model = "none"

        return {
            "app_env":     cfg.APP_ENV,
            "app_version": cfg.APP_VERSION,
            "database":    db_stats,
            "llm": {
                "available":    llm_ok,
                "active_model": llm_model,
            },
            "features": {
                "voice":        cfg.FEATURE_VOICE,
                "translation":  cfg.FEATURE_TRANSLATION,
                "ocr":          cfg.FEATURE_OCR,
                "reminders":    cfg.FEATURE_REMINDERS,
                "appointments": cfg.FEATURE_APPOINTMENTS,
            },
        }


# ── Module-level singleton ────────────────────────────────────────────────────
container = _Container()
