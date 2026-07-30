"""
database/migrations/init_schema.py — Backward-compatible entry point.
Delegates to the versioned migration runner.

Run directly: python database/migrations/init_schema.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from database.migrations.runner import run_migrations

if __name__ == "__main__":
    run_migrations()
