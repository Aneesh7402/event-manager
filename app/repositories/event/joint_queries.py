from sqlalchemy import and_
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.models import Recurrence
from app.db.models.events import Event, EventAccess, EventInfo
from app.schemas.api.events import CombinedEventResponse, EventFilterRequest, EventFilterResponse


def get_filtered_events_paginated(
    db: Session, filters: EventFilterRequest,user_id: int
) -> EventFilterResponse:
    base_query = (
        db.query(Event, EventInfo, EventAccess)
        .join(EventInfo, Event.event_id == EventInfo.id)
        .join(EventAccess, Event.event_id == EventAccess.event_id)
    )

    query_filters = [EventAccess.user_id == user_id]

    if filters.title:
        query_filters.append(EventInfo.title.ilike(f"%{filters.title}%"))
    if filters.location:
        query_filters.append(EventInfo.location.ilike(f"%{filters.location}%"))
    if filters.status:
        query_filters.append(Event.status == filters.status)
    if filters.access:
        query_filters.append(EventAccess.access == filters.access)

    filtered_query = base_query.filter(and_(*query_filters))

    # Count total records before pagination
    total_count = filtered_query.count()

    # Apply sorting
    sort_column_map = {
        "start_time": Event.start_time,
        "end_time": Event.end_time,
        "title": EventInfo.title,
        "location": EventInfo.location,
        "status": Event.status,
    }
    sort_column = sort_column_map.get(filters.sort_by, Event.start_time)
    order_fn = asc if filters.sort_order == "asc" else desc
    sorted_query = filtered_query.order_by(order_fn(sort_column))

    # Apply pagination
    results = sorted_query.limit(filters.limit).offset(filters.offset).all()

    events = [
        CombinedEventResponse(
            event_id=e.event_id,
            start_time=e.start_time,
            end_time=e.end_time,
            status=e.status,
            title=ei.title,
            description=ei.description,
            location=ei.location,
            access=ea.access,
        )
        for e, ei, ea in results
    ]

    return EventFilterResponse(
        events=events,
        total_count=total_count,
        final_offset=filters.offset + len(events),
    )


def save_event_info(db: Session, event_info: EventInfo):
    db.add(event_info)


def save_event(db: Session, event: Event):
    db.add(event)


def save_recurrence(db: Session, recurrence: Recurrence):
    db.add(recurrence)

