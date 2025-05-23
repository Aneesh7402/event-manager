from collections import defaultdict
from datetime import timedelta

from fastapi import HTTPException

from app.middleware.middleware import logger
from app.repositories import event as event_repo
from app.repositories.event import *
from app.repositories.event.change_log import get_change_logs_by_version

from app.schemas.api import events
from app.schemas.api.events import *
from app.services.events import validate_event_update_conditions, validate_duration_against_recurrence
from app.utils import AccessLevel, parse_typed_value, cast_value, get_interval_seconds


def create_event_service(
    payload: events.EventCreate, db: Session,user_id: int
) -> tuple[EventInfo, Event]:

    # 1. Insert into event_info
    event_info_obj = create_event_info(
        db,
        EventInfoCreate(
            title=payload.title, desc=payload.description, location=payload.location
        ),
    )  # gets event_info.id before commit

    # 2. Insert into events
    event_obj = create_event(
        db,
        EventCreateInternal(
            event_id=event_info_obj.id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        ),
    )

    # 3. Insert into event_access
    access = create_event_access(
        db,
        EventAccessCreate(
            user_id=user_id,
            event_id=event_info_obj.id,
            access=AccessLevel.OWNER,
        ),
    )

    # 4. Optional: handle recurrence
    if payload.is_recurring and payload.recurrence_pattern:
        recurrence = create_recurrence(
            db,
            RecurrenceCreate(
                event_id=event_info_obj.id,
                pattern=payload.recurrence_pattern,
                duration=int((payload.end_time - payload.start_time).total_seconds()),
            ),
        )

    return event_info_obj, event_obj

def share_event_service(db: Session, event_id: int, payload: ShareEventPayload):
    shared_entries = []

    for user in payload.users:
        existing_access = get_access_by_user_and_event(db, user_id=user.user_id, event_id=event_id)

        if existing_access:
            updated_access = update_event_access(db, existing_access, user.role)
            shared_entries.append(EventAccessResponse(user_id=updated_access.user_id, access=updated_access.access))
        else:
            new_access = create_event_access(
                db,
                EventAccessCreate(user_id=user.user_id, event_id=event_id, access=user.role)
            )
            shared_entries.append(EventAccessResponse(user_id=new_access.user_id, access=new_access.access))

    return shared_entries




def update_event_info_fields(event_info: EventInfo, payload: EventUpdatePayload,updated_fields:dict):
    if payload.title is not None:
        updated_fields["title"] = event_info.title,payload.title
        event_info.title = payload.title

    if payload.description is not None:
        updated_fields["description"] = event_info.description,payload.description
        event_info.description = payload.description

    if payload.location is not None:
        updated_fields["location"] = event_info.location,payload.location
        event_info.location = payload.location

    event_info.version+=1



def update_event_fields(event: Event, payload: EventUpdatePayload, updated_fields:dict):
    if payload.start_time is not None:
        updated_fields["start_time"] = event.start_time,payload.start_time
        event.start_time = payload.start_time
    if payload.end_time is not None:
        updated_fields["end_time"] = event.end_time,payload.end_time
        event.end_time = payload.end_time

def update_recurrence(
    db: Session,
    event_id: int,
    recurrence: Recurrence | None,
    payload: EventUpdatePayload,
    event: Event,
    updated_fields: dict
):
    if not event.start_time or not event.end_time:
        raise HTTPException(status_code=400, detail="Start and end time required for recurrence")

    duration = int((event.end_time - event.start_time).total_seconds())
    r_payload = payload.recurrence

    # Check and update recurrence if it exists
    if recurrence:
        if r_payload.hour is not None and r_payload.hour != recurrence.hour:
            updated_fields["recurrence_hour"] = (recurrence.hour, r_payload.hour)
            recurrence.hour = r_payload.hour

        if r_payload.day is not None and r_payload.day != recurrence.day:
            updated_fields["recurrence_day"] = (recurrence.day, r_payload.day)
            recurrence.day = r_payload.day

        if r_payload.month is not None and r_payload.month != recurrence.month:
            updated_fields["recurrence_month"] = (recurrence.month, r_payload.month)
            recurrence.month = r_payload.month

        if r_payload.year is not None and r_payload.year != recurrence.year:
            updated_fields["recurrence_year"] = (recurrence.year, r_payload.year)
            recurrence.year = r_payload.year
    else:
        raise HTTPException(status_code=400, detail="Cannot add recurrence to a one-time scheduled event. Please create a new one with recurrence.")

    event_repo.save_recurrence(db, recurrence)


def update_event_details_service(event_id: int, payload: EventUpdatePayload, db: Session) -> (dict,int):
    updated_fields = {}  # Dictionary to hold old_value, new_value pairs for updated fields
    try:
        event_info = event_repo.get_event_info_by_id(db, event_id)
        event = event_repo.get_event_by_event_id(db, event_id)
        validate_event_update_conditions(event, event_info, payload)

        update_event_info_fields(event_info, payload,updated_fields)
        # update_event_fields(event, payload,updated_fields)

        event_repo.save_event_info(db, event_info)
        # event_repo.save_event(db, event)

        recurrence = event_repo.get_recurrence_by_event_id(db, event_id)
        if payload.recurrence is not None:
            update_recurrence(db, event_id, recurrence, payload, event,updated_fields)
        if recurrence:
            validate_duration_against_recurrence(event, recurrence)

        db.commit()
        return updated_fields,event_info.version

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def populate_change_log(db: Session, updated_fields: dict, version: int,event_id:int) -> bool:
    try:
        # Loop over each updated field in the dictionary
        for field_name, (old_val, new_val) in updated_fields.items():
            # Create a new ChangeLog entry for each updated field
            change_log_entry = ChangeLog(
                event_id=event_id,  # Use the event_id (or another identifier) here
                new_version_id=version,  # Assuming new_version_id is the same as version
                field_name=field_name,
                old_val=old_val,  # The old value of the field
                new_val=new_val   # The new value of the field
            )

            # Add the change log entry to the session
            db.add(change_log_entry)

        # Commit the transaction to save the entries in the database
        db.commit()

        # Return True indicating success
        return True

    except Exception as e:
        # Rollback the session in case of any errors
        db.rollback()
        # Log the error for debugging purposes
        raise Exception(f"Error populating change log: {str(e)}")

def delete_event_by_id(db: Session, event_id: int) -> bool:
    try:
        # 1. Delete ChangeLogs
        change_logs = get_change_logs_by_event(db, event_id)
        for change_log in change_logs:
            db.delete(change_log)


        # 2. Delete EventAccess
        accesses = get_accesses_by_event(db, event_id)
        for access in accesses:
            db.delete(access)


        # 3. Delete Events
        events = db.query(Event).filter(Event.event_id == event_id).all()
        for event in events:
            db.delete(event)


        # 4. Delete Recurrence (if any)
        recurrence = get_recurrence_by_event_id(db, event_id)
        if recurrence:
            db.delete(recurrence)
        db.commit()  # Stage 4

        # 5. Finally, delete EventInfo
        event_info = get_event_info_by_id(db, event_id)
        if event_info:
            db.delete(event_info)
        db.commit()  # Stage 5

        return True

    except Exception as e:
        logger.error(f"Error deleting event info: {str(e)}")
        db.rollback()
        return False



def delete_event_permission(db: Session, event_id: int, user_id: int) -> bool:
    permission = get_access_by_user_and_event(db, user_id, event_id)
    if not permission:
        return False

    db.delete(permission)
    db.commit()
    return True

def get_difference(
    db: Session, event_id: int, from_version: int, to_version: int
) -> dict:
    difference = {}

    for version in range(from_version + 1, to_version + 1):
        logs = get_change_logs_by_version(db, event_id, version)

        for log in logs:
            field = log.field_name
            old_val = str(log.old_val) if log.old_val is not None else None
            new_val = str(log.new_val) if log.new_val is not None else None

            if field in difference:
                # Update only the new_val
                difference[field][1] = new_val
            else:
                # First time the field is seen
                difference[field] = [old_val, new_val]

    return difference

def reconstruct_event_version(
    db: Session, event_id: int, version_id: int
) -> dict:
    # Step 1: Get current event info and recurrence
    event_info = get_event_info_by_id(db, event_id)
    recurrence = get_recurrence_by_event_id(db, event_id)
    if not event_info:
        raise HTTPException(status_code=404, detail="Event not found.")

    # Step 2: Turn current values into a mutable dict
    base = {
        "id": event_info.id,
        "title": event_info.title,
        "description": event_info.description,
        "location": event_info.location,
        "version": version_id,
        "recurrence_hour": recurrence.hour if recurrence else 0,
        "recurrence_day": recurrence.day if recurrence else 0,
        "recurrence_month": recurrence.month if recurrence else 0,
        "recurrence_year": recurrence.year if recurrence else 0,
    }

    # Step 2: Apply cumulative changes
    diff = get_difference(db, event_id=event_info.id, from_version=version_id, to_version=event_info.version)

    for field, (old_val, _) in diff.items():
        base[field] = parse_typed_value(field, old_val)

    # Step 3: Post-process to get the final structured format
    reconstructed = {
        "id": base["id"],
        "title": base["title"],
        "description": base["description"],
        "location": base["location"],
        "version": base["version"],
        "recurrence": {
            "hour": base.get("recurrence_hour", 0),
            "day": base.get("recurrence_day", 0),
            "month": base.get("recurrence_month", 0),
            "year": base.get("recurrence_year", 0),
        }
    }

    return reconstructed


def rollback_event_to_version_service(
    db: Session,
    event_id: int,
    target_version: int,
    current_version: int
):
    difference = get_difference(db, event_id, from_version=target_version, to_version=current_version)

    event_info = get_event_info_by_id(db, event_id)
    recurrence = get_recurrence_by_event_id(db, event_id)

    #Loop through fields in dict, check which entities have the field, update the field and break for that field
    for field, (old_val, _) in difference.items():
        for entity in (event_info, recurrence):
            if entity and hasattr(entity, field):
                current_val = getattr(entity, field)
                casted_val = cast_value(type(current_val), old_val)
                setattr(entity, field, casted_val)
                break
    delete_change_logs_from_version_onwards(db, event_id, target_version+1)
    event_info.version = target_version

    event_repo.save_event_info(db, event_info)
    if recurrence:
        event_repo.save_recurrence(db, recurrence)

    db.commit()

#For chronological ordering of logs
def get_event_changelog(db: Session, event_id: int) -> EventChangelogResponse:
    logs = get_change_logs_by_event(db, event_id)

    version_map = defaultdict(list)

    for log in logs:

        version_map[log.new_version_id].append(ChangeLogEntry(
            field_name=str(log.field_name),
            old_val=str(log.old_val if log.old_val is not None else None),
            new_val=str(log.new_val if log.new_val is not None else None),
        ))

    changelog = [
        EventVersionChangeLog(version=version, changes=changes)
        for version, changes in sorted(version_map.items())
    ]

    return EventChangelogResponse(event_id=event_id, changelog=changelog)

def add_next_event(
    db: Session,
    event_id: int,
) -> Event | None:
    # Fetch the original event
    event = get_event_by_event_id(db, event_id)
    if not event:
        return None

    # Fetch the recurrence pattern
    recurrence = get_recurrence_by_event_id(db, event_id)
    if not recurrence:
        return None
    original_start = event.start_time

    pattern_delta = timedelta(seconds=get_interval_seconds(RecurrencePattern(hour=recurrence.hour, day=recurrence.day, month=recurrence.month,year=recurrence.year)))
    new_start = original_start + pattern_delta
    new_end = new_start + timedelta(seconds=recurrence.duration)

    # Create new EventInfo
    new_event=create_event(db, EventCreateInternal(
        event_id=event_id,
    start_time=new_start,
    end_time=new_end))

    return new_event
