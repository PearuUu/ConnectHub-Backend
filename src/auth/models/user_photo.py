from typing import TYPE_CHECKING
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer

if TYPE_CHECKING:
    from src.auth.models.user import User

class UserPhoto(Base):
    __tablename__ = "user_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    photo_url: Mapped[str] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="photos")
