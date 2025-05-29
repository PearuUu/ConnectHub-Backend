from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Table, ForeignKey, Column
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from hobby.models.category import Category

user_hobby_association = Table(
    "user_hobby",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("hobby_id", ForeignKey("hobbies.id"), primary_key=True)
)


class Hobby(Base):
    __tablename__ = "hobbies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(
        foreign_keys=[category_id], back_populates="hobbies")

    def __repr__(self):
        return f"<Hobby(id={self.id}, name={self.name})>"
