from pydantic import BaseModel

SESSION_EXPIRATION_MS = 1800000
# 30 minutes in milliseconds
class RecurrencePattern(BaseModel):
    hour: int
    day: int
    month: int
    year: int

# Define the topics you want to create
TOPICS_TO_CREATE= ["event_start", "event_end", "send_notif"]