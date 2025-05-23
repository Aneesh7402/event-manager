from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from datetime import datetime, timezone
from app.db.base import Base

class ChangeLog(Base):
    __tablename__ = "change_log"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("event_info.id"), index=True, nullable=False)
    new_version_id = Column(Integer, nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    old_val = Column(Text)  # Can store None, Integer, String, or Datetime
    new_val = Column(Text)  # Can store None, Integer, String, or Datetime
    changed_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __init__(self, event_id: int, new_version_id: int, field_name: str, old_val=None, new_val=None):
        self.event_id = event_id
        self.new_version_id = new_version_id
        self.field_name = field_name
        # Convert the values to string if they are not None
        self.old_val = self._convert_to_str(old_val)
        self.new_val = self._convert_to_str(new_val)
        self.changed_at = datetime.now(timezone.utc)

    def _convert_to_str(self, value):
        """
        Helper method to convert values to string for storage.
        Handles None, Integer, String, and Datetime.
        """
        if isinstance(value, (str, int)):  # Handle String and Integer
            return str(value)
        elif isinstance(value, datetime):  # Handle Datetime
            return value.isoformat()  # Store datetime in ISO format
        elif value is None:  # Handle None
            return None
        return str(value)