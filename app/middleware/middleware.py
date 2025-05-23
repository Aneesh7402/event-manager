from fastapi import Request, HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.repositories.auth import get_active_session_by_user_id
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

ALLOWED_PREFIXES = ["/api/events","/api/auth/refresh","/api/auth/logout"]  # Routes to apply token validation

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.bearer = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next):
        db_gen = get_db()
        db = next(db_gen)
        try:
            path = request.url.path

            if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
                credentials: HTTPAuthorizationCredentials = await self.bearer(request)
                if not credentials or credentials.scheme.lower() != "bearer":
                    return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})

                try:
                    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = payload.get("user_id")
                    if not user_id:
                        return JSONResponse(status_code=401, content={"detail": "user_id missing in token"})

                    session = get_active_session_by_user_id(db=db, user_id=user_id)
                    if not session:
                        return JSONResponse(status_code=401, content={"detail": "Session doesn't exist"})
                    expiration = session.token_expiration_timestamp
                    if expiration.tzinfo is None:
                        expiration = expiration.replace(tzinfo=timezone.utc)
                    if expiration <= datetime.now(timezone.utc):
                        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
                    if session.token != credentials.credentials:
                        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

                    request.state.user_id = user_id

                except JWTError as jwt_err:
                    logger.warning(f"JWT error: {jwt_err}")
                    return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.exception(f"Internal server error during auth middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error occurred. Please contact support."}
            )
        finally:
            db_gen.close()
