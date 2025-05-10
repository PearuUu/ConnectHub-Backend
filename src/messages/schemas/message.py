from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageSchema(BaseModel):
    id: int
    text: str
    photo_url: Optional[str]
    timestamp: datetime
    sender_id: int
    receiver_id: int

    class Config:
        orm_mode = True
