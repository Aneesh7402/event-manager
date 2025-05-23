from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username=Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True,nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)

    def __init__(self, username:str, email: str, hashed_password: str, phone_number: str | None = None):
        self.email = email
        self.hashed_password = hashed_password
        self.phone_number = phone_number
        self.username=username
