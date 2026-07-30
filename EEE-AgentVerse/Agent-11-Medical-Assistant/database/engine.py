"""
database/engine.py — DatabaseManager: connection lifecycle, WAL pragmas,
backup/recovery, integrity checks, and session factory.

Backward-compatible shims
─────────────────────────
  get_session()  ← context-manager, unchanged.
  init_db()      ← unchanged.
"""
from __future__ import annotations

import shutil
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL, DB_ECHO, DB_PATH
from utils.logger import get_logger

log = get_logger(__name__)


class DatabaseManager:
    """
    Manages the SQLAlchemy engine and session factory.
    Thread-safe singleton; call get_db_manager() to access it.
    """

    def __init__(self, url: str = DATABASE_URL, echo: bool = DB_ECHO) -> None:
        self._url  = url
        self._lock = threading.Lock()
        self._sessions_opened: int = 0
        self._sessions_closed: int = 0

        self._engine = create_engine(
            url,
            echo=echo,
            connect_args={"check_same_thread": False},
        )
        self._apply_pragmas()
        self._SessionLocal = sessionmaker(
            bind=self._engine, autocommit=False, autoflush=False
        )
        log.info("DatabaseManager initialised: %s", url)

    # ── SQLite pragmas ────────────────────────────────────────────────────────
    def _apply_pragmas(self) -> None:
        @event.listens_for(self._engine, "connect")
        def _set_pragmas(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.execute("PRAGMA cache_size=-64000")   # 64 MB page cache
            cur.execute("PRAGMA temp_store=MEMORY")
            cur.execute("PRAGMA mmap_size=268435456")  # 256 MB mmap
            cur.execute("PRAGMA wal_autocheckpoint=1000")
            cur.close()

    # ── Session context-manager ───────────────────────────────────────────────
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        db: Session = self._SessionLocal()
        with self._lock:
            self._sessions_opened += 1
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
            with self._lock:
                self._sessions_closed += 1

    # ── Schema bootstrap ──────────────────────────────────────────────────────
    def init_db(self) -> None:
        from database.models import Base
        Base.metadata.create_all(bind=self._engine)
        log.info("Database schema initialised.")

    # ── Health check ──────────────────────────────────────────────────────────
    def health_check(self) -> bool:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            log.error("Database health check failed: %s", exc)
            return False

    # ── Integrity check ───────────────────────────────────────────────────────
    def integrity_check(self) -> bool:
        """Run SQLite integrity_check and foreign_key_check. Returns True if clean."""
        try:
            db_path = self._db_file_path()
            if db_path is None:
                return True  # in-memory or non-SQLite
            conn = sqlite3.connect(str(db_path))
            try:
                ic = conn.execute("PRAGMA integrity_check").fetchone()
                fk = conn.execute("PRAGMA foreign_key_check").fetchall()
            finally:
                conn.close()
            if ic[0] != "ok":
                log.error("integrity_check failed: %s", ic[0])
                return False
            if fk:
                log.error("foreign_key_check violations: %s", fk)
                return False
            return True
        except Exception as exc:
            log.error("integrity_check error: %s", exc)
            return False

    # ── Backup ────────────────────────────────────────────────────────────────
    def backup(self, backup_dir: Path | None = None) -> Path | None:
        """
        Hot backup using SQLite's online backup API (safe while DB is in use).
        Checkpoints WAL first, then copies via sqlite3.Connection.backup().
        Returns the backup file path, or None on failure.
        """
        db_path = self._db_file_path()
        if db_path is None:
            log.warning("backup() skipped: not a file-based SQLite database.")
            return None
        try:
            dest_dir = backup_dir or db_path.parent / "backups"
            dest_dir.mkdir(parents=True, exist_ok=True)
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = dest_dir / f"{db_path.stem}_{ts}.db"

            # Checkpoint WAL so backup is fully consistent
            with self._engine.connect() as conn:
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))

            src  = sqlite3.connect(str(db_path))
            bkp  = sqlite3.connect(str(dest))
            try:
                src.backup(bkp)
            finally:
                bkp.close()
                src.close()

            log.info("Backup created: %s", dest)
            return dest
        except Exception as exc:
            log.error("Backup failed: %s", exc)
            return None

    # ── Recovery ─────────────────────────────────────────────────────────────
    def recover_from_backup(self, backup_path: Path) -> bool:
        """
        Replace the live database with a backup file.
        Disposes the engine first to release all connections, then copies,
        then re-initialises the engine.
        """
        db_path = self._db_file_path()
        if db_path is None:
            log.error("recover_from_backup() only works with file-based SQLite.")
            return False
        if not backup_path.exists():
            log.error("Backup file not found: %s", backup_path)
            return False
        try:
            self._engine.dispose()
            shutil.copy2(str(backup_path), str(db_path))
            # Re-create engine after restore
            self._engine = create_engine(
                self._url,
                echo=DB_ECHO,
                connect_args={"check_same_thread": False},
            )
            self._apply_pragmas()
            self._SessionLocal.configure(bind=self._engine)
            log.info("Recovered database from: %s", backup_path)
            return True
        except Exception as exc:
            log.error("Recovery failed: %s", exc)
            return False

    # ── Stats ─────────────────────────────────────────────────────────────────
    def stats(self) -> dict:
        return {
            "url":             self._url,
            "sessions_opened": self._sessions_opened,
            "sessions_closed": self._sessions_closed,
            "sessions_active": self._sessions_opened - self._sessions_closed,
            "healthy":         self.health_check(),
        }

    # ── Engine access ─────────────────────────────────────────────────────────
    @property
    def engine(self):
        return self._engine

    # ── Internal helper ───────────────────────────────────────────────────────
    def _db_file_path(self) -> Path | None:
        """Extract the file path from a sqlite:/// URL, or None."""
        if not self._url.startswith("sqlite:///"):
            return None
        raw = self._url[len("sqlite:///"):]
        if not raw or raw == ":memory:":
            return None
        return Path(raw)


# ── Module-level singleton ────────────────────────────────────────────────────
_db_manager: DatabaseManager | None = None
_db_lock = threading.Lock()


def get_db_manager() -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        with _db_lock:
            if _db_manager is None:
                _db_manager = DatabaseManager()
    return _db_manager


# ── Backward-compatible shims ─────────────────────────────────────────────────
@contextmanager
def get_session() -> Generator[Session, None, None]:
    with get_db_manager().session() as session:
        yield session


def init_db() -> None:
    get_db_manager().init_db()
