from pydantic import BaseModel
from typing import Optional


class EventInfoCreate(BaseModel):
    title: str
    desc: Optional[str] = None
    location: Optional[str] = None

