from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.mysql import VARCHAR

from app.db.base import Base
from datetime import datetime, timedelta

class ActiveSession(Base):
    __tablename__ = "active_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token_expiration_timestamp = Column(DateTime, nullable=False)
    token = Column(VARCHAR(250), nullable=False)

    def __init__(self, user_id: int, token: str, token_expiration_timestamp: datetime):
        self.user_id = user_id
        self.token = token
        self.token_expiration_timestamp = token_expiration_timestamp
