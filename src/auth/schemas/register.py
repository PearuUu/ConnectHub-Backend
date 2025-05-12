from pydantic import BaseModel


class RegisterResponse(BaseModel):

    user_id: int
    email: str

    model_config = {
        "from_attributes": True
    }
