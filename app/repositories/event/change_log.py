# app/db/repositories/change_log.py
from typing import Any

from sqlalchemy.orm import Session
from app.db.models.events.change_log import ChangeLog


def create_change_log(
    db: Session,
    event_id: int,
    new_version_id: int,
    field_name: str,
    old_val,
    new_val,
) -> ChangeLog:
    change = ChangeLog(
        event_id=event_id,
        new_version_id=new_version_id,
        field_name=field_name,
        old_val=old_val,
        new_val=new_val,
    )
    db.add(change)
    db.commit()
    db.refresh(change)
    return change


def create_bulk_change_logs(
    db: Session,
    changes: list[dict],
) -> list[ChangeLog]:
    logs = [
        ChangeLog(
            event_id=change["event_id"],
            new_version_id=change["new_version_id"],
            field_name=change["field_name"],
            old_val=change.get("old_val"),
            new_val=change.get("new_val"),
        )
        for change in changes
    ]
    db.add_all(logs)
    db.commit()
    return logs


def get_change_logs_by_event(
    db: Session, event_id: int
) -> list[type[ChangeLog]]:
    return db.query(ChangeLog).filter(ChangeLog.event_id == event_id).order_by(ChangeLog.new_version_id.asc(), ChangeLog.id.asc()).all()


def get_change_logs_by_version(
    db: Session, event_id: int, version_id: int
) -> list[type[ChangeLog]]:
    return (
        db.query(ChangeLog)
        .filter(
            ChangeLog.event_id == event_id,
            ChangeLog.new_version_id == version_id,
        )
        .all()
    )
def delete_change_logs_from_version_onwards(
    db: Session, event_id: int, version_id: int
) -> int:
    """
    Deletes all change log entries for the given event_id from the given version_id (inclusive) onwards.
    Returns the number of rows deleted.
    """
    deleted = (
        db.query(ChangeLog)
        .filter(
            ChangeLog.event_id == event_id,
            ChangeLog.new_version_id >= version_id,
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted