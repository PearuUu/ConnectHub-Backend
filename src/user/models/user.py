from typing import List, Optional
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column


from src.models import Base

if TYPE_CHECKING:
    from user.models.user_photo import UserPhoto
    from match.models.userLiked import UserLiked
    from messages.models.message import Message


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Relationships (lazy loaded by default)
    # hobbies: Mapped[List["UserHobby"]] = relationship(back_populates="user")
    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", 
        foreign_keys="Message.sender_id",
        back_populates="sender"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message", 
        foreign_keys="Message.receiver_id",
        back_populates="receiver"
    )
    liked_users: Mapped[List["UserLiked"]] = relationship(
        "UserLiked", 
        foreign_keys="UserLiked.liker_id",
        back_populates="liker"
    )
    liked_by_users: Mapped[List["UserLiked"]] = relationship(
        "UserLiked", 
        foreign_keys="UserLiked.liked_id",
        back_populates="liked"
    )
    photos: Mapped[List["UserPhoto"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, login={self.login}, email={self.email})>"