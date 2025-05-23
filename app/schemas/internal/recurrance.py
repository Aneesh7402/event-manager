from pydantic import BaseModel

from app.utils import RecurrencePattern


class RecurrenceCreate(BaseModel):
    event_id: int
    pattern: RecurrencePattern
    duration: int  # duration in minutes or seconds (your choice)


