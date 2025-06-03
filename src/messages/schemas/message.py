from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageSchema(BaseModel):
    id: int
    text: str
    photo_url: Optional[str] = None
    timestamp: datetime
    sender_id: int
    receiver_id: int

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    text: str
    photo_url: Optional[str] = None
    receiver_id: int
    # sender_id will be from the authenticated user
    # timestamp will be auto-generated

    class Config:
        orm_mode = True


class MessageUpdate(BaseModel):
    text: Optional[str] = None
    # photo_url: Optional[str] = None # Decide if photo URL can be updated this way
    # Other fields like sender_id, receiver_id, timestamp are generally not updatable.

    class Config:
        orm_mode = True
