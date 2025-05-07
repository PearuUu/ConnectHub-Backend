from typing import TYPE_CHECKING
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer

if TYPE_CHECKING:
    from src.user.models.user import User

class UserPhoto(Base):
    __tablename__ = "user_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    photo_url: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="photos")

    def __repr__(self):
        return f"<UserPhoto(id={self.id}, user_id={self.user_id}, photo_url={self.photo_url})>"
