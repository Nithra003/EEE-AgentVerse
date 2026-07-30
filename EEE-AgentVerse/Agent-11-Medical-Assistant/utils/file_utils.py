"""
utils/file_utils.py — Image save/load/cleanup helpers.
"""
from __future__ import annotations

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import UPLOAD_DIR
from utils.logger import get_logger

log = get_logger(__name__)


def save_upload(file_bytes: bytes, original_name: str) -> Path:
    """
    Save uploaded bytes to UPLOAD_DIR with a timestamped unique name.
    Returns the saved Path.
    """
    suffix = Path(original_name).suffix.lower() or ".jpg"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    digest = hashlib.md5(file_bytes).hexdigest()[:8]
    filename = f"{ts}_{digest}{suffix}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(file_bytes)
    log.debug("Saved upload: %s (%d bytes)", dest, len(file_bytes))
    return dest


def load_image_bytes(path: Path) -> Optional[bytes]:
    """Read image bytes; return None if file missing."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        log.warning("Image not found: %s", path)
        return None


def delete_file(path: Path) -> bool:
    """Delete a file; return True on success."""
    try:
        path.unlink(missing_ok=True)
        return True
    except Exception as exc:
        log.error("Could not delete %s: %s", path, exc)
        return False


def cleanup_old_uploads(max_age_days: int = 30) -> int:
    """Remove uploads older than max_age_days. Returns count deleted."""
    cutoff = datetime.now().timestamp() - max_age_days * 86400
    deleted = 0
    for f in UPLOAD_DIR.iterdir():
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink(missing_ok=True)
            deleted += 1
    log.info("Cleaned up %d old uploads.", deleted)
    return deleted
