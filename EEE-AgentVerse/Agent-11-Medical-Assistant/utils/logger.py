"""
utils/logger.py — LogManager: structured, context-aware rotating logger.

Optimisation: handlers are attached once to the root "app" logger.
All child loggers (app.ocr, app.ai, …) inherit them — no per-module
file handles, no duplicate log lines.

Backward compatibility
──────────────────────
  get_logger(__name__)  ← still works everywhere, unchanged.
"""
from __future__ import annotations

import json
import logging
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

from config import LOG_DIR, LOG_LEVEL, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_FORMAT

_TEXT_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_context_local = threading.local()
_root_configured = False
_root_lock = threading.Lock()


class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ctx: Dict[str, Any] = getattr(_context_local, "fields", {})
        payload: Dict[str, Any] = {
            "ts":      datetime.utcnow().isoformat() + "Z",
            "level":   record.levelname,
            "logger":  record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        payload.update(ctx)
        return json.dumps(payload, ensure_ascii=False)


def _configure_root() -> None:
    """Attach handlers to the shared 'app' root logger exactly once."""
    global _root_configured
    if _root_configured:
        return
    with _root_lock:
        if _root_configured:
            return

        level     = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
        use_json  = LOG_FORMAT == "json"
        formatter = _JSONFormatter() if use_json else logging.Formatter(_TEXT_FMT, datefmt=_DATE_FMT)

        root = logging.getLogger("app")
        root.setLevel(level)
        root.propagate = False

        if not root.handlers:
            # Console
            ch = logging.StreamHandler(sys.stderr)
            ch.setFormatter(formatter)
            root.addHandler(ch)

            # Rotating app log
            fh = RotatingFileHandler(
                LOG_DIR / "app.log",
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding="utf-8",
            )
            fh.setFormatter(formatter)
            root.addHandler(fh)

            # Rotating error log (ERROR+ only)
            eh = RotatingFileHandler(
                LOG_DIR / "error.log",
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding="utf-8",
            )
            eh.setLevel(logging.ERROR)
            eh.setFormatter(formatter)
            root.addHandler(eh)

        _root_configured = True


class LogManager:
    """Central log manager with per-request context support."""

    def get_logger(self, name: str) -> logging.Logger:
        """Return a child of the shared 'app' logger (idempotent)."""
        _configure_root()
        # Map arbitrary module names to app.* hierarchy
        child_name = f"app.{name}" if not name.startswith("app.") else name
        logger = logging.getLogger(child_name)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        return logger

    def set_context(self, **fields: Any) -> None:
        existing: Dict[str, Any] = getattr(_context_local, "fields", {})
        existing.update(fields)
        _context_local.fields = existing

    def clear_context(self) -> None:
        _context_local.fields = {}

    def get_context(self) -> Dict[str, Any]:
        return dict(getattr(_context_local, "fields", {}))

    def set_level(self, level: str) -> None:
        new_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger("app").setLevel(new_level)


_log_manager = LogManager()


def get_log_manager() -> LogManager:
    return _log_manager


def get_logger(name: str) -> logging.Logger:
    """Backward-compatible shim — every existing call works unchanged."""
    return _log_manager.get_logger(name)
