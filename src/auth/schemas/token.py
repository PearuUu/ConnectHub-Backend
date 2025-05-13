from pydantic import BaseModel
from typing import Optional


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

    class Config:
        orm_mode = True
