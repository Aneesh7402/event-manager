from sqlalchemy import Column, String, ForeignKey, DateTime, Enum,Integer
from datetime import datetime
from app.db.base import Base
from app.utils import EventStatus


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("event_info.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.SCHEDULED)

    def __init__(self, event_id:int, start_time: datetime, end_time: datetime, status: EventStatus = EventStatus.SCHEDULED):
        self.event_id = event_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
