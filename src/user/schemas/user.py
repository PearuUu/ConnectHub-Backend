from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

from src.auth.schemas.password import PasswordBase, PasswordChange
from .user_photo import UserPhotoSchema


class UserSchema(BaseModel):
    id: int
    login: str
    email: EmailStr
    phone_number: Optional[str] = None
    first_name: str
    last_name: str
    # Added to match service loading behavior
    
    profile_photo: Optional[UserPhotoSchema] = None

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserSearch(BaseModel):
    id: Optional[int] = None
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(PasswordBase):
    login: str
    email: EmailStr
    phone_number: Optional[str] = None
    first_name: str
    last_name: str
