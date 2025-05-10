from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

    class Config:
        orm_mode = True
