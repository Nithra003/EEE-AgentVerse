"""database/migrations/m001_init_schema.py — Initial schema bootstrap."""
from sqlalchemy.orm import Session

from database.models import Base
from database.engine import get_db_manager


def upgrade(session: Session) -> None:
    Base.metadata.create_all(bind=get_db_manager().engine)
