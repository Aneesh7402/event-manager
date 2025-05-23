from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

# Get Kafka configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "abc")  # Default to localhost:9092
ALGORITHM = os.getenv("ALGORITHM", "HS256") 

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["iat"] = int(time.time())  # issued at (current timestamp in seconds)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
