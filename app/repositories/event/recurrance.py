from typing import Any

from sqlalchemy.orm import Session
from app.db.models.events.recurrance import Recurrence
from app.schemas import RecurrenceCreate

def create_recurrence(db: Session, rec: RecurrenceCreate)->Recurrence:
    db_rec = Recurrence(
        event_id=rec.event_id,
        hour=rec.pattern.hour,
        day=rec.pattern.day,
        month=rec.pattern.month,
        year=rec.pattern.year,
        duration=rec.duration,
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

def get_recurrence_by_event_id(db: Session, event_id: int)-> Recurrence | None:
    return db.query(Recurrence).filter(Recurrence.event_id == event_id).first()
