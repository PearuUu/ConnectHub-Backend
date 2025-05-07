
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from src.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from hobby.models.category import Category
class Hobby(Base):
    __tablename__ = "hobbies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="hobbies")
    