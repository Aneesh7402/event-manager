from pydantic import BaseModel
from app.utils.event_status import AccessLevel



class EventAccessCreate(BaseModel):
    user_id: str
    event_id: str
    access: AccessLevel
