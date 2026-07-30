"""
database/migrations/runner.py — Versioned migration runner.

Usage:
    python database/migrations/runner.py
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Callable

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from database.engine import get_db_manager
from database.models import SchemaVersion
from utils.logger import get_logger

log = get_logger(__name__)

# Ordered list of (version_id, module_name, description)
MIGRATIONS: list[tuple[str, str, str]] = [
    ("001", "database.migrations.m001_init_schema",   "Initial schema bootstrap"),
    ("002", "database.migrations.m002_add_indexes",   "Add composite indexes"),
]


def _applied_versions(session) -> set[str]:
    return {row.version for row in session.query(SchemaVersion).all()}


def run_migrations() -> None:
    mgr = get_db_manager()
    mgr.init_db()  # ensure schema_versions table exists

    with mgr.session() as session:
        applied = _applied_versions(session)

    for version, module_name, description in MIGRATIONS:
        if version in applied:
            log.info("Migration %s already applied, skipping.", version)
            continue

        log.info("Applying migration %s: %s", version, description)
        try:
            mod = importlib.import_module(module_name)
            upgrade: Callable = getattr(mod, "upgrade")
            with mgr.session() as session:
                upgrade(session)
                session.add(SchemaVersion(version=version, description=description))
            log.info("Migration %s applied successfully.", version)
            print(f"  ✅ {version}: {description}")
        except Exception as exc:
            log.error("Migration %s failed: %s", version, exc)
            print(f"  ❌ {version}: {exc}")
            raise


if __name__ == "__main__":
    print("Running migrations...")
    run_migrations()
    print("Done.")
