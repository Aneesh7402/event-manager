from croniter import croniter
from datetime import datetime, timedelta


from app.schemas.api.events import EventVersionResponse
from app.utils import RecurrencePattern


def get_interval_seconds(expr: RecurrencePattern) -> int:
    """Returns the recurrence interval in seconds based on the given pattern."""
    seconds = 0
    seconds += expr.year * 365 * 24 * 60 * 60  # approx, doesn't account for leap years
    seconds += expr.month * 30 * 24 * 60 * 60  # approx month duration
    seconds += expr.day * 24 * 60 * 60
    seconds += expr.hour * 60 * 60
    return seconds

def map_to_event_version_response(data: dict) -> EventVersionResponse:
    return EventVersionResponse(
        id=data["id"],
        title=data["title"],
        description=data.get("description"),
        location=data.get("location"),
        version=data["version"],
        recurrence=RecurrencePattern(
            hour=data["recurrence"]["hour"],
            day=data["recurrence"]["day"],
            month=data["recurrence"]["month"],
            year=data["recurrence"]["year"],
        )
    )
def parse_typed_value(field: str, val: str):
    if val is None:
        return None
    if field in {"hour", "day", "month", "year"}:
        return int(val)
    if field in {"id", "version"}:
        return int(val)
    if field.endswith("_time"):  # e.g., start_time, end_time
        return datetime.fromisoformat(val)
    return val  # for str fields like title, location

def cast_value(target_type, value: str):
    if value is None:
        return None
    try:
        if target_type == int:
            return int(value)
        elif target_type == str:
            return value
        elif target_type == datetime:
            return datetime.fromisoformat(value)
        return value
    except Exception:
        raise ValueError(f"Failed to cast {value} to {target_type}")


def get_message(topic, event_id, timestamp):
    """Generate a subject and body message based on the topic, event_id, and timestamp."""

    # Define the subject and body for different topics
    if topic == "event_start":
        subject = f"Event {event_id} Started"
        body = f"Event {event_id} has started. The event is now live."

    elif topic == "event_end":
        subject = f"Event {event_id} Ended"
        body = f"Event {event_id} has ended. Thank you for attending!"

    elif topic == "send_notif":
        subject = f"Event {event_id} Updated"
        body = f"Event {event_id} has been updated at {timestamp}. Please check for the latest changes."

    else:
        subject = "Unknown Event"
        body = "There is no information available for the specified event topic."

    return subject, body

