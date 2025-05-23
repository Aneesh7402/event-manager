from typing import Optional

from pydantic import BaseModel, EmailStr,field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str
    
    @field_validator('phone_number')
    @classmethod
    def validate_indian_phone(cls, v):
        if not v.isdigit():
            raise ValueError("Phone number must contain digits only")
        if len(v) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if v[0] not in {'6', '7', '8', '9'}:
            raise ValueError("Phone number must start with 6, 7, 8, or 9")
        return v

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: str

    model_config = {
    "from_attributes": True
}

class UserWithToken(BaseModel):
    user: UserOut
    token: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserOut] = None

class LogoutUserResponse(BaseModel):
    success: bool