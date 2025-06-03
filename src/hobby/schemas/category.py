from pydantic import BaseModel
from typing import List
from .hobby import HobbySchema


class CategoryCreate(BaseModel):
    name: str


class CategorySchema(BaseModel):
    id: int
    name: str
    hobbies: List[HobbySchema] = []

    class Config:
        orm_mode = True
