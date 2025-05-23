from sqlalchemy import Column, ForeignKey, Enum,Integer

from enum import Enum as PyEnum
import uuid
from app.db.base import Base
from app.utils import AccessLevel


class EventAccess(Base):
    __tablename__ = "event_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"),index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("event_info.id"), index=True,nullable=False)
    access = Column(Enum(AccessLevel), nullable=False, default=AccessLevel.READ)

    def __init__(self, user_id, event_id, access: AccessLevel = AccessLevel.WRITE):
        self.user_id = user_id
        self.event_id = event_id
        self.access = access
