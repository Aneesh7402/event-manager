from datetime import datetime,timezone
from fastapi import HTTPException, status

from app.db.models import EventInfo, Recurrence,Event
from app.schemas import RecurrencePattern
from app.schemas.api.events import EventCreate, EventUpdatePayload
from app.utils import EventStatus
from app.utils.functions import get_interval_seconds

def validate_event_times(payload: EventCreate):
    now_utc = datetime.now(timezone.utc)

    if payload.start_time < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time cannot be in the past."
        )

    if payload.end_time <= payload.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be greater than start time."
        )

def validate_recurrence(payload: EventCreate):
    if not payload.recurrence_pattern:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence pattern required for recurring events."
        )

    try:
        interval_seconds = get_interval_seconds(payload.recurrence_pattern)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cron string: {str(e)}"
        )

    duration_seconds = (payload.end_time - payload.start_time).total_seconds()

    if interval_seconds <= duration_seconds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recurrence interval must be greater than the event duration."
        )

def validate_event_update_conditions(event: Event | None, event_info: EventInfo | None, payload: EventUpdatePayload):
    if not event_info:
        raise HTTPException(status_code=404, detail="EventInfo not found")

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status in {EventStatus.COMPLETED, EventStatus.CANCELLED}:
        raise HTTPException(status_code=400, detail="Cannot update a completed or cancelled event")

    if event.status == EventStatus.ACTIVE and payload.start_time is not None:
        raise HTTPException(status_code=400, detail="Cannot modify start time of an active event")

def validate_duration_against_recurrence(event: Event, recurrence: Recurrence):
    if event.start_time and event.end_time:
        duration_seconds = (event.end_time - event.start_time).total_seconds()
        interval_seconds = get_interval_seconds(
            RecurrencePattern(
                hour=recurrence.hour,
                day=recurrence.day,
                month=recurrence.month,
                year=recurrence.year,
            )
        )
        if duration_seconds > interval_seconds:
            raise HTTPException(
                status_code=400,
                detail="Event duration is shorter than recurrence interval",
            )