from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.schemas.api.user import UserCreate, UserWithToken, Token, UserLogin, LogoutUserResponse
from app.db.session import get_db
from app.repositories.auth import *
from app.core.security import create_access_token, verify_password
from datetime import timezone

router = APIRouter()


@router.post("/register", response_model=UserWithToken)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_phone(db,user_in.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    if get_user_by_username(db,user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    user = create_user(
        db,
        user_in
    )
    token = create_access_token(data={"sub": user.email,"user_id":user.id})
    create_active_session(db=db,user_id=user.id,token=token)

    return {"user": user, "token": token}



@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Retrieve user from DB using email or username
    db_user = get_user_by_username(db, user.username)

    if db_user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    session=get_active_session_by_user_id(db, db_user.id)
    # Check if session exists and if the token is still valid
    expiration = session.token_expiration_timestamp if session else None
    if expiration and expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    if session and expiration > datetime.now(timezone.utc):
        update_active_session(db,db_user.id,session.token)
        return {
            "access_token": session.token,
            "token_type": "bearer",
            "user": db_user
        }

    # If session is invalid or doesn't exist, create a new access token
    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})
    update_active_session(db=db, user_id=db_user.id, new_token=access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/refresh")
def refresh(request:Request, db: Session = Depends(get_db)):
    # Retrieve user from DB using email or username
    user_id = request.state.user_id

    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    update_active_session(db=db, user_id=user_id)
    return {
        "success": True,
    }


@router.post("/logout", response_model=LogoutUserResponse)
def refresh(request:Request,db: Session = Depends(get_db)):
    # Retrieve user from DB using email or username
    user_id = request.state.user_id

    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    delete_active_session(db=db, user_id=user_id)
    return LogoutUserResponse(success=True)

