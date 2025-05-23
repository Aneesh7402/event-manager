from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.auth.user import User
from app.core.security import SECRET_KEY,ALGORITHM

# OAuth2PasswordBearer helps in extracting token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Dependency to get the user from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        # Decode the token to extract the user information (sub will be the email in this case)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no username (sub) claim",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Query the user from the database using the extracted username (email in this case)
        user = db.query(User).filter(User.email == username).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
