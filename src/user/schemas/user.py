from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .user_photo import UserPhotoSchema

class UserSchema(BaseModel):
    id: int
    login: str
    #password: str
    email: EmailStr
    phone_number: Optional[str]
    first_name: str
    last_name: str
    photos: List[UserPhotoSchema] = []

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: str
    phone_number: Optional[str]
    first_name: str
    last_name: str

