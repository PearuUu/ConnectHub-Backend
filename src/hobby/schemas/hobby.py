from typing import Optional
from pydantic import BaseModel


class HobbySchema(BaseModel):
    id: Optional[int] = None
    name: str
    category_id: int

    class Config:
        orm_mode = True


class HobbyCreate(BaseModel):
    name: str
    category_id: int

    class Config:
        orm_mode = True


class HobbyUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        orm_mode = True
