from sqlalchemy.orm import Session
from app.db.models.events.events import Event
from app.schemas import EventCreateInternal
from typing import List, Any

from app.utils import EventStatus


def create_event(db: Session, event: EventCreateInternal)->Event:
    db_event = Event(
        event_id=event.event_id,
        start_time=event.start_time,
        end_time=event.end_time,
        status=event.status
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_event_by_event_id(db: Session, event_id: int) -> Event|None:
    return db.query(Event).filter(Event.event_id == event_id and Event.status==str(EventStatus.SCHEDULED)).first()

def get_events_in_time_range(db: Session, start, end) -> list[type[Event]]:
    return db.query(Event).filter(Event.start_time >= start, Event.start_time < end).all()

def get_first_scheduled_event(db: Session, event_id: int) -> Event|None:
    db.query(Event).filter(Event.id == event_id, Event.status == "SCHEDULED").first()