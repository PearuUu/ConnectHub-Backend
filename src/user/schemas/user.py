from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .user_photo import UserPhotoSchema

class UserSchema(BaseModel):
    id: int
    login: str
    email: EmailStr
    phone_number: Optional[str]
    first_name: str
    last_name: str
    photos: List[UserPhotoSchema] = []

    class Config:
        orm_mode = True
