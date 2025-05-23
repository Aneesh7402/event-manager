from sqlalchemy.orm import Session
from app.db.models.events.event_info import EventInfo
from app.schemas import EventInfoCreate

def create_event_info(db: Session, event: EventInfoCreate)->EventInfo:
    db_event = EventInfo(
        title=event.title,
        description=event.desc,
        location=event.location,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_event_info_by_id(db: Session, event_id: int)->EventInfo|None:
    return db.query(EventInfo).filter(EventInfo.id == event_id).first()

def get_all_event_info(db: Session):
    return db.query(EventInfo).all()
