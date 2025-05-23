from sqlalchemy.orm import Session
from app.db.models.events import EventAccess
from app.schemas import EventAccessCreate
from app.utils import AccessLevel
from typing import List


def create_event_access(db: Session, access: EventAccessCreate)->EventAccess:
    db_access = EventAccess(
        user_id=access.user_id,
        event_id=access.event_id,
        access=access.access
    )
    db.add(db_access)
    db.commit()
    db.refresh(db_access)
    return db_access

def update_event_access(db: Session, db_access: EventAccess, new_access_level: AccessLevel) -> EventAccess:
    db_access.access = new_access_level
    db.commit()
    db.refresh(db_access)
    return db_access

def get_access_by_user_and_event(db: Session, user_id: int, event_id: int):
    return db.query(EventAccess).filter(EventAccess.user_id == user_id, EventAccess.event_id == event_id).first()

def get_accesses_by_event(db: Session, event_id: int)->List[EventAccess]:
    return db.query(EventAccess).filter(EventAccess.event_id == event_id).all()








