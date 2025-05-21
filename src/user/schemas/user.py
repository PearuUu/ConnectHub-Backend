from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

from src.auth.schemas.password import PasswordBase, PasswordChange
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


class UserCreate(PasswordBase):
    login: str
    email: EmailStr
    phone_number: Optional[str] = None  # Add default value of None
    first_name: str
    last_name: str
