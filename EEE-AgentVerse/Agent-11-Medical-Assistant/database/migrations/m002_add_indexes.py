"""database/migrations/m002_add_indexes.py — Add composite indexes."""
from sqlalchemy import text
from sqlalchemy.orm import Session

# Each tuple: (index_name, CREATE INDEX statement)
_INDEXES = [
    ("ix_prescriptions_user_created",
     "CREATE INDEX IF NOT EXISTS ix_prescriptions_user_created ON prescriptions (user_id, created_at)"),
    ("ix_medicines_user_active",
     "CREATE INDEX IF NOT EXISTS ix_medicines_user_active ON medicines (user_id, end_date)"),
    ("ix_reminders_user_status",
     "CREATE INDEX IF NOT EXISTS ix_reminders_user_status ON reminders (user_id, status)"),
    ("ix_reminders_user_time",
     "CREATE INDEX IF NOT EXISTS ix_reminders_user_time ON reminders (user_id, remind_time)"),
    ("ix_reminder_logs_reminder_action",
     "CREATE INDEX IF NOT EXISTS ix_reminder_logs_reminder_action ON reminder_logs (reminder_id, action)"),
    ("ix_reminder_logs_fired_at",
     "CREATE INDEX IF NOT EXISTS ix_reminder_logs_fired_at ON reminder_logs (fired_at)"),
    ("ix_appointments_user_date",
     "CREATE INDEX IF NOT EXISTS ix_appointments_user_date ON appointments (user_id, apt_date)"),
    ("ix_appointments_user_status",
     "CREATE INDEX IF NOT EXISTS ix_appointments_user_status ON appointments (user_id, status)"),
    ("ix_conv_user_session",
     "CREATE INDEX IF NOT EXISTS ix_conv_user_session ON conversation_history (user_id, session_id)"),
    ("ix_conv_session_created",
     "CREATE INDEX IF NOT EXISTS ix_conv_session_created ON conversation_history (session_id, created_at)"),
]


def upgrade(session: Session) -> None:
    for _name, ddl in _INDEXES:
        session.execute(text(ddl))
