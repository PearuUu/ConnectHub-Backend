from models import Base

class Token(Base):
    access_token: str
    token_type: str
    refresh_token: str