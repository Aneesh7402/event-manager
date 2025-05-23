from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.kafka_config import send_notification
from app.db.session import get_db
from app.repositories.auth import are_all_user_ids_present
from app.repositories.event import get_access_by_user_and_event, get_event_by_event_id, get_event_info_by_id, \
    get_filtered_events_paginated, get_accesses_by_event, get_recurrence_by_event_id
from app.schemas.api.events import EventCreate, EventResponse, EventResponseWithAccess, ShareEventPayload, \
    ShareEventResponse, EventFilterResponse, EventFilterRequest, EventUpdatePayload, BatchEventCreate, \
    PermissionResponse, EventVersionResponse, EventChangelogResponse
from app.services.events import update_event_details_service, delete_event_by_id, delete_event_permission, \
    rollback_event_to_version_service, reconstruct_event_version, get_difference, populate_change_log
from app.services.events.event_service import create_event_service, share_event_service,get_event_changelog
from app.services.events.validations import validate_event_times, validate_recurrence
from app.utils import AccessLevel, map_to_event_version_response, RecurrencePattern

router = APIRouter()

@router.post("", response_model=EventFilterResponse, status_code=status.HTTP_200_OK)
def filter_events(
    filters: EventFilterRequest,
request: Request,
    db: Session = Depends(get_db),

):
    """
    Fetch paginated, filtered list of events with metadata (total count and final offset).
    """
    user_id = request.state.user_id  # Extracted from middleware
    return get_filtered_events_paginated(db=db, filters=filters,user_id=user_id)

# --- routers/event.py ---
@router.post("/create", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db), request: Request = None):
    validate_event_times(payload)
    if payload.is_recurring:
        validate_recurrence(payload)

    user_id = request.state.user_id  # Extracted from JWT by middleware
    event_info, event = create_event_service(payload, db, user_id=user_id)

    return EventResponse(
        id=event_info.id,
        title=event_info.title,
        description=event_info.description,
        location=event_info.location,
        start_time=event.start_time,
        end_time=event.end_time
    )


@router.post("/batch", response_model=List[EventResponse], status_code=status.HTTP_201_CREATED)
def create_events_batch(
    payload: BatchEventCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    user_id = request.state.user_id
    responses = []
    for event_payload in payload.events:                #Looping 2 times, first time to ensure valid data.
        validate_event_times(event_payload)                 # Handling it here instead of service layer
        if event_payload.is_recurring:                              #to reuse functions
            validate_recurrence(event_payload)

    for event_payload in payload.events:
        event_info, event = create_event_service(event_payload, db, user_id=user_id)

        responses.append(EventResponse(
            id=event_info.id,
            title=event_info.title,
            description=event_info.description,
            location=event_info.location,
            start_time=event.start_time,
            end_time=event.end_time
        ))

    return responses

#only returns latest event instance
@router.get("/{id}", response_model=EventResponseWithAccess)
def get_event(id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id  # Extracted from middleware

    # Check if user has access to this event
    access_entry = get_access_by_user_and_event(db, user_id=user_id, event_id=id)
    if not access_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this event."
        )

    event_info, event ,recurrence =get_event_info_by_id(db,id), get_event_by_event_id(db, id),get_recurrence_by_event_id(db, id)
    if not event_info or not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )

    return EventResponseWithAccess(
        id=event_info.id,
        title=event_info.title,
        description=event_info.description,
        location=event_info.location,
        start_time=event.start_time,
        end_time=event.end_time,
        access=access_entry.access,
        status=event.status,
        version=event_info.version,
        recurrence_pattern=RecurrencePattern(
            hour=recurrence.hour,
            day=recurrence.day,
            year=recurrence.year,
            month=recurrence.month
        ) if recurrence else None
    )





#Omitting changing start_time and end_time in this iteration due to overcomplication when it comes to recurring events
@router.put("/{event_id}", summary="Update event details")
def update_event(
    event_id: int,
    payload: EventUpdatePayload,
request: Request,
    db: Session = Depends(get_db),
):
    """
    Update the details of an event (e.g., title, time, recurrence).
    """
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, event_id)
    if not access or (access.access not in [AccessLevel.OWNER, AccessLevel.WRITE]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this event."
        )

    changed_values,version = update_event_details_service(event_id, payload, db)
    if not changed_values:
        raise HTTPException(status_code=500, detail="Failed to update event")
    populate_change_log(db,changed_values,version,event_id)
    
    send_notification("send_notif", {"event_id": event_id})
    return {"message": "Event updated successfully"}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(id: int, request:Request ,db: Session = Depends(get_db)):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, id)
    if not access or access.access != AccessLevel.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this event."
        )
    success = delete_event_by_id(db=db, event_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or could not be deleted."
        )

@router.put("/{id}/share",response_model=ShareEventResponse, status_code=status.HTTP_200_OK)
def share_event(
    id: int,
request: Request,
    payload: ShareEventPayload,
    db: Session = Depends(get_db),

):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, id)
    
    if not access or access.access != AccessLevel.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can share this event. If owner, please check existence of the event"
        )
    if not are_all_user_ids_present(db,[user.user_id for user in payload.users]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid User_ID provided. Please check again"
        )
    for user in payload.users:
        if user.user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot share this event with yourself."
            )
    # Input validations can go here if needed
    return ShareEventResponse(users=share_event_service(db, id, payload))

@router.get("/{id}/permissions", response_model=List[PermissionResponse])
def list_event_permissions(id: int, db: Session = Depends(get_db), request: Request = None):

    permissions = get_accesses_by_event(db, id)
    return [
        PermissionResponse(user_id=perm.user_id, access=perm.access)
        for perm in permissions
    ]

@router.delete("/{id}/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_event_permission(id: int, user_id: int, db: Session = Depends(get_db), request: Request = None):

    # Authorization: Only OWNER can remove permissions
    requester_id = request.state.user_id
    access = get_access_by_user_and_event(db, requester_id, id)
    if not access or access.access != AccessLevel.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can manage permissions")

    # Prevent removing your own OWNER access
    if requester_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove your own OWNER access")

    deleted = delete_event_permission(db, id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Permission not found")

    return  # 204 No Content

@router.get("/{event_id}/history/{version_id}", response_model=EventVersionResponse)
def get_event_at_version(event_id: int, version_id: int,request:Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, event_id)

    if not access:
        raise HTTPException(status_code=403, detail="You do not have permission to view history of this event.")

    event_dict = reconstruct_event_version(db, event_id, version_id)
    return map_to_event_version_response(event_dict)


@router.post("/{event_id}/rollback/{version_id}", status_code=200)
def rollback_event(
    event_id: int,
    version_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, event_id)

    if not access or access.access == AccessLevel.READ:
        raise HTTPException(status_code=403, detail="You do not have permission to rollback this event.")

    event_info_obj = get_event_info_by_id(db, event_id)
    if version_id >= event_info_obj.version:
        raise HTTPException(status_code=400, detail="Cannot rollback to current or future version")

    try:
        rollback_event_to_version_service(db, event_id, version_id, event_info_obj.version)
        return {"detail": f"Rolled back to version {version_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}/changelog", response_model=EventChangelogResponse, status_code=200)
def get_event_changelog_route(id: int,request: Request, db: Session = Depends(get_db), ):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, id)

    if not access:
        raise HTTPException(status_code=403, detail="You do not have permission to view changelogs of this event.")

    result = get_event_changelog(db, id)
    if not result.changelog:
        raise HTTPException(status_code=404, detail="No changelog found for event.")
    return result

@router.get("/events/{event_id}/diff/{version1}/{version2}")
def get_event_version_diff(
request: Request,
    event_id: int,
    version1: int,
    version2: int,
    db: Session = Depends(get_db),
):
    user_id = request.state.user_id
    access = get_access_by_user_and_event(db, user_id, event_id)

    if not access:
        raise HTTPException(status_code=403, detail="You do not have permission to view changelogs of this event.")

    if version1 >= version2:
        raise HTTPException(status_code=400, detail="version1 must be less than version2")

    try:
        diff = get_difference(db, event_id, version1, version2)
        return diff
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

