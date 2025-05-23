from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from app.db.base import Base

class ChangeLog(Base):
    __tablename__ = "change_log"
    id = Column(Integer, primary_key=True)
    table_name = Column(String)
    row_id = Column(String)
    operation = Column(String)
    changed_fields = Column(JSON)
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(String)
    changed_at = Column(DateTime(timezone=True), default=func.now())
