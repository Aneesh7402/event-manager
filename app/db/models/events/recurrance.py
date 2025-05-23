from sqlalchemy import Column, ForeignKey, BigInteger,Integer


from app.db.base import Base

class Recurrence(Base):
    __tablename__ = "recurrence"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("event_info.id"), unique=True,index=True, nullable=False)
    hour = Column(Integer,default=0,nullable=False)
    day = Column(Integer, default=0, nullable=False)
    month=  Column(Integer,default=0, nullable=False)
    year=  Column(Integer,default=0, nullable=False)
    duration = Column(BigInteger, nullable=False)  # e.g. 1800 for 30 minutes in seconds

    def __init__(self, event_id:int , hour:int, day: int,month: int,year :int, duration: int):
        self.event_id = event_id
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year
        self.duration = duration
