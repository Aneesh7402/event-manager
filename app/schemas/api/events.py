from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


from app.utils import AccessLevel, RecurrencePattern
from app.utils import EventStatus


class EventCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    is_recurring: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    location: Optional[str]
    start_time: datetime
    end_time: datetime

    model_config = {
    "from_attributes": True
}

class BatchEventCreate(BaseModel):
    events: List[EventCreate]


class EventResponseWithAccess(BaseModel):
    id: int
    title: str
    description: str
    location: Optional[str]
    start_time: datetime
    end_time: datetime
    version:int
    access: str  # e.g., owner/read/write
    status: str
    recurrence_pattern: Optional[RecurrencePattern]
    
    model_config = {
        "from_attributes": True
    }

class ShareEventUser(BaseModel):
    user_id: int
    role: AccessLevel

    @field_validator('role')
    @classmethod
    def disallow_owner(cls, value):
        if value == AccessLevel.OWNER:
            raise ValueError("Role 'owner' is not allowed when sharing events.")
        return value
    # should be validated to be one of allowed roles elsewhere

class ShareEventPayload(BaseModel):
    users: List[ShareEventUser]

class EventAccessResponse(BaseModel):
    user_id:int
    access:str


class ShareEventResponse(BaseModel):
    users: List[EventAccessResponse]



class CombinedEventResponse(BaseModel):
    # From Event
    event_id: int
    start_time: datetime
    end_time: datetime
    status: EventStatus

    # From EventInfo
    title: str
    description: Optional[str] = None
    location: Optional[str] = None

    # From EventAccess
    access: AccessLevel

    model_config = {
        "from_attributes": True
    }
class EventFilterResponse(BaseModel):
    events: List[CombinedEventResponse]
    total_count: int
    final_offset: int

class EventFilterRequest(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    status: Optional[EventStatus] = None
    access: Optional[AccessLevel] = None
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)
    sort_by: Optional[str] = "start_time"
    sort_order: Optional[str] = "asc"  # "asc" or "desc"


class EventUpdatePayload(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    recurrence: Optional[RecurrencePattern] = None


class PermissionResponse(BaseModel):
    user_id: int
    access: str

class EventVersionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    version: int
    recurrence: RecurrencePattern

class ChangeLogEntry(BaseModel):
    field_name: str
    old_val: Optional[str]
    new_val: Optional[str]

class EventVersionChangeLog(BaseModel):
    version: int
    changes: List[ChangeLogEntry]

class EventChangelogResponse(BaseModel):
    event_id: int
    changelog: List[EventVersionChangeLog]