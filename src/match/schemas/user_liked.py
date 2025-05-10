from pydantic import BaseModel

class UserLikedSchema(BaseModel):
    liker_id: int
    liked_id: int

    class Config:
        orm_mode = True
