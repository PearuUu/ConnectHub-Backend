from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from hobby.models.category import Category
class Hobby(Base):
    __tablename__ = "hobbies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(foreign_keys=[category_id], back_populates="hobbies")

    def __repr__(self):
        return f"<Hobby(id={self.id}, name={self.name})>"
