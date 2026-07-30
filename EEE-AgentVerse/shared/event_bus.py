"""
shared/event_bus.py — File-backed JSON event bus with atomic writes and file locking.
Fixed: race condition, data corruption on write failure, atomic save via temp file.
"""

import json
import os
import tempfile
from datetime import datetime
from typing import Any

_BUS_FILE = os.path.join(os.path.dirname(__file__), "events.json")

# Cross-process file lock using a lock file
_LOCK_FILE = _BUS_FILE + ".lock"


def _acquire_lock():
    """Simple spin-lock using a lock file. Returns lock fd."""
    import time
    for _ in range(50):  # max 5 seconds
        try:
            fd = os.open(_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            return fd
        except FileExistsError:
            time.sleep(0.1)
    # Stale lock — remove and retry once
    try:
        os.remove(_LOCK_FILE)
    except OSError:
        pass
    fd = os.open(_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    return fd


def _release_lock(fd):
    try:
        os.close(fd)
        os.remove(_LOCK_FILE)
    except OSError:
        pass


def _load() -> list:
    if os.path.exists(_BUS_FILE):
        try:
            with open(_BUS_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save(events: list) -> None:
    """Atomic write: write to temp file then rename — prevents corruption."""
    data = json.dumps(events[-200:], indent=2, ensure_ascii=False)
    dir_ = os.path.dirname(_BUS_FILE)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
            os.replace(tmp_path, _BUS_FILE)
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise
    except Exception:
        pass  # never crash the calling agent


# ── Public API ────────────────────────────────────────────────────────────────

def publish(event_type: str, source: str, payload: dict[str, Any]) -> None:
    """Append one event to the bus (thread/process safe)."""
    lock_fd = _acquire_lock()
    try:
        events = _load()
        events.append({
            "type":      event_type,
            "source":    source,
            "payload":   payload,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read_by":   [],
        })
        _save(events)
    finally:
        _release_lock(lock_fd)


def subscribe(event_type: str, consumer: str) -> list[dict]:
    """Return unread events of *event_type* for *consumer*, mark them read."""
    lock_fd = _acquire_lock()
    try:
        events = _load()
        result = []
        for ev in events:
            if ev["type"] == event_type and consumer not in ev.get("read_by", []):
                result.append(ev)
                ev.setdefault("read_by", []).append(consumer)
        if result:
            _save(events)
        return result
    finally:
        _release_lock(lock_fd)


def latest(event_type: str, n: int = 5) -> list[dict]:
    """Return the *n* most recent events of *event_type* (read or unread)."""
    return [e for e in reversed(_load()) if e["type"] == event_type][:n]
