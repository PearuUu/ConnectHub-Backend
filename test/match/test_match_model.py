import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.match.models.userLiked import UserLiked


async def test_user_liked_model(db: AsyncSession):
    user_liked = UserLiked(liker_id=1, liked_id=2)
    db.add(user_liked)
    await db.commit()
    await db.refresh(user_liked)

    assert user_liked.liker_id == 1
    assert user_liked.liked_id == 2
