"""
reminder/scheduler.py — APScheduler setup with SQLite job store.
Provides a singleton BackgroundScheduler used by ReminderService.
"""
from __future__ import annotations

import threading
from typing import Callable, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from config import DB_PATH
from utils.logger import get_logger

log = get_logger(__name__)

_scheduler: Optional[BackgroundScheduler] = None
_lock = threading.Lock()


def get_scheduler() -> BackgroundScheduler:
    """Return the module-level singleton scheduler (lazy init + start)."""
    global _scheduler
    with _lock:
        if _scheduler is None:
            jobstore_url = f"sqlite:///{DB_PATH}"
            _scheduler = BackgroundScheduler(
                jobstores={"default": SQLAlchemyJobStore(url=jobstore_url)},
                executors={"default": ThreadPoolExecutor(max_workers=4)},
                job_defaults={"coalesce": True, "max_instances": 1, "misfire_grace_time": 300},
            )
            try:
                _scheduler.start()
                log.info("APScheduler started with SQLite job store.")
            except Exception as exc:
                log.error("APScheduler failed to start: %s", exc)
    return _scheduler


def add_daily_job(
    job_id: str,
    func: Callable,
    hour: int,
    minute: int,
    args: Optional[list] = None,
) -> bool:
    """Add or replace a daily cron job. Returns True on success."""
    try:
        sched = get_scheduler()
        sched.add_job(
            func,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=job_id,
            args=args or [],
            replace_existing=True,
        )
        log.info("Scheduled daily job %s at %02d:%02d", job_id, hour, minute)
        return True
    except Exception as exc:
        log.error("Failed to add daily job %s: %s", job_id, exc)
        return False


def add_weekly_job(
    job_id: str,
    func: Callable,
    day_of_week: str,   # "mon,fri" etc.
    hour: int,
    minute: int,
    args: Optional[list] = None,
) -> bool:
    """Add or replace a weekly cron job."""
    try:
        sched = get_scheduler()
        sched.add_job(
            func,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id=job_id,
            args=args or [],
            replace_existing=True,
        )
        log.info("Scheduled weekly job %s on %s at %02d:%02d", job_id, day_of_week, hour, minute)
        return True
    except Exception as exc:
        log.error("Failed to add weekly job %s: %s", job_id, exc)
        return False


def add_once_job(
    job_id: str,
    func: Callable,
    run_at,   # datetime
    args: Optional[list] = None,
) -> bool:
    """Schedule a one-time job."""
    try:
        sched = get_scheduler()
        sched.add_job(
            func,
            trigger=DateTrigger(run_date=run_at),
            id=job_id,
            args=args or [],
            replace_existing=True,
        )
        log.info("Scheduled one-time job %s at %s", job_id, run_at)
        return True
    except Exception as exc:
        log.error("Failed to add one-time job %s: %s", job_id, exc)
        return False


def pause_job(job_id: str) -> bool:
    try:
        get_scheduler().pause_job(job_id)
        return True
    except Exception as exc:
        log.warning("Could not pause job %s: %s", job_id, exc)
        return False


def resume_job(job_id: str) -> bool:
    try:
        get_scheduler().resume_job(job_id)
        return True
    except Exception as exc:
        log.warning("Could not resume job %s: %s", job_id, exc)
        return False


def remove_job(job_id: str) -> bool:
    try:
        get_scheduler().remove_job(job_id)
        return True
    except Exception as exc:
        log.warning("Could not remove job %s: %s", job_id, exc)
        return False
