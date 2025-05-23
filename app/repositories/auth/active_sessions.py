from typing import Any

from sqlalchemy.orm import Session
from app.db.models.auth import ActiveSession
from datetime import datetime, timedelta,timezone

from app.utils import SESSION_EXPIRATION_MS


# Function to create a new session with expiration from constant
def create_active_session(db: Session, user_id: int, token: str) -> ActiveSession:
    token_expiration_timestamp = datetime.now(timezone.utc) + timedelta(seconds=SESSION_EXPIRATION_MS / 1000)  # Convert ms to seconds
    db_session = ActiveSession(
        user_id=user_id,
        token=token,
        token_expiration_timestamp=token_expiration_timestamp
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# Function to fetch session by user_id
def get_active_session_by_user_id(db: Session, user_id: int) -> type[ActiveSession] | None:
    return db.query(ActiveSession).filter(ActiveSession.user_id == user_id).first()

# Function to update session token and expiration timestamp by user_id

def update_active_session(db: Session, user_id: int, new_token: str = None) -> ActiveSession | None:
    new_token_expiration = datetime.now(timezone.utc) + timedelta(
        seconds=SESSION_EXPIRATION_MS / 1000)  # Convert ms to seconds

    # Check if the session already exists
    db_session = db.query(ActiveSession).filter(ActiveSession.user_id == user_id).first()

    if db_session:
        # Update existing session
        if new_token:
            db_session.token = new_token
        db_session.token_expiration_timestamp = new_token_expiration
        db.commit()
        db.refresh(db_session)
    else:
        # Create a new session if none exists
        db_session = ActiveSession(
            user_id=user_id,
            token=new_token,
            token_expiration_timestamp=new_token_expiration
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)

    return db_session


# Function to delete session by user_id
def delete_active_session(db: Session, user_id: int) -> None:
    db_session = db.query(ActiveSession).filter(ActiveSession.user_id == user_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()


