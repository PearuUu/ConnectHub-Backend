from pydantic import BaseModel

class UserPhotoSchema(BaseModel):
    id: int
    user_id: int
    photo_url: str

    class Config:
        orm_mode = True
