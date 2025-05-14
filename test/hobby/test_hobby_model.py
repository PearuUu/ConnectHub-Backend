import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.hobby.models.hobby import Hobby


async def test_hobby_model(db: AsyncSession):
    hobby = Hobby(name="Football", category_id=1)
    db.add(hobby)
    await db.commit()
    await db.refresh(hobby)

    assert hobby.id is not None
    assert hobby.name == "Football"
