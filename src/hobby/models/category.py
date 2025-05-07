from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, String
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from hobby.models.hobby import Hobby

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    hobbies: Mapped[List["Hobby"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"