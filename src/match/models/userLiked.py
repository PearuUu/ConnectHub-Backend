
from typing import TYPE_CHECKING
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from src.user.models.user import User


class UserLiked(Base):
    __tablename__ = "user_likes"

    liker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    liked_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    liker: Mapped["User"] = relationship(foreign_keys=[liker_id],back_populates="liked_users")
    liked: Mapped["User"] = relationship(foreign_keys=[liked_id],back_populates="liked_by_users")