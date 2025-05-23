from pydantic import BaseModel

from datetime import datetime
from typing import Optional
from app.utils.event_status import EventStatus

class EventCreateInternal(BaseModel):
    event_id: int
    start_time: datetime
    end_time: datetime
    status: Optional[EventStatus]=EventStatus.SCHEDULED

