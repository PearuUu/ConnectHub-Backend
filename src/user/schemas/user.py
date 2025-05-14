from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

from src.auth.schemas.password import PasswordChange
from .user_photo import UserPhotoSchema


class UserSchema(BaseModel):
    id: int
    login: str
    # password: str
    email: EmailStr
    phone_number: Optional[str]
    first_name: str
    last_name: str
    photos: List[UserPhotoSchema] = []

    model_config = {
        "from_attributes": True
    }


class UserCreate(PasswordChange):
    login: str
    email: EmailStr
    phone_number: Optional[str]
    first_name: str
    last_name: str

    