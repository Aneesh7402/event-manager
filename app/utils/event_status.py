from enum import Enum

class AccessLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    OWNER = "owner"

class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
