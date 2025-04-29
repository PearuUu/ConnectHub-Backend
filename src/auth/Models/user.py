from sqlalchemy import Column, Integer, String
from src.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
    phone_number = Column(String)
    first_name = Column(String)
    last_name = Column(String)