from git import Optional
from pydantic import BaseModel

class HobbySchema(BaseModel):
    id: Optional[int] = None
    name: str
    category_id: int

    class Config:
        orm_mode = True
