from pydantic import BaseModel
from app.utils.event_status import AccessLevel



class EventAccessCreate(BaseModel):
    user_id: int
    event_id: int
    access: AccessLevel
