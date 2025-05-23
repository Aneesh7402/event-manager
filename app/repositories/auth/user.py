from sqlalchemy.orm import Session, Query
from app.db.models.auth.user import User
from app.schemas.api.user import UserCreate
from app.core.security import hash_password
from typing import List, Set, Any


def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        phone_number=user.phone_number,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users_by_ids(db: Session, ids: Set[int]) -> list[type[User]]:
    return db.query(User).filter(User.id.in_(ids)).all()

def are_all_user_ids_present(db: Session, user_ids: List[int]) -> bool:
    count = db.query(User.id).filter(User.id.in_(user_ids)).count()
    return count == len(user_ids)