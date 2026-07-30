# utils/__init__.py
# ── Logger ────────────────────────────────────────────────────────────────────
from utils.logger import get_logger, get_log_manager, LogManager

# ── Error handling ────────────────────────────────────────────────────────────
from utils.error_handler import (
    safe_execute,
    format_user_error,
    get_exception_handler,
    GlobalExceptionHandler,
    AppError,
    ErrorCode,
)

# ── Validators ────────────────────────────────────────────────────────────────
from utils.validators import (
    validate_username, validate_password, validate_age,
    validate_phone, validate_date_string, validate_time_string,
    validate_medicine_name, validate_duration_days, sanitize_text,
)

# ── Date / time helpers ───────────────────────────────────────────────────────
from utils.date_utils import (
    parse_date, parse_time, format_date, format_time,
    today_str, now_str, days_until, add_days,
    medicine_end_date, is_past, friendly_date,
)

# ── File helpers ──────────────────────────────────────────────────────────────
from utils.file_utils import save_upload, load_image_bytes, delete_file

__all__ = [
    # Logger
    "get_logger", "get_log_manager", "LogManager",
    # Error handling
    "safe_execute", "format_user_error", "get_exception_handler",
    "GlobalExceptionHandler", "AppError", "ErrorCode",
    # Validators
    "validate_username", "validate_password", "validate_age",
    "validate_phone", "validate_date_string", "validate_time_string",
    "validate_medicine_name", "validate_duration_days", "sanitize_text",
    # Date / time
    "parse_date", "parse_time", "format_date", "format_time",
    "today_str", "now_str", "days_until", "add_days",
    "medicine_end_date", "is_past", "friendly_date",
    # File
    "save_upload", "load_image_bytes", "delete_file",
]
