from sqlalchemy import Column, String,Integer

from app.db.base import Base

class EventInfo(Base):
    __tablename__ = "event_info"

    id = Column(Integer, primary_key=True,index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    version = Column(Integer,default=1 ,nullable=False)

    def __init__(self, title: str, description: str = "", location: str = None):
        self.title = title
        self.description = description
        self.location = location
