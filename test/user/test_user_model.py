import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.models.user import User


async def test_user_model(db: AsyncSession):
    user = User(
        login="testuser",
        email="testuser@example.com",
        password="hashedpassword",
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    assert user.id is not None
    assert user.login == "testuser"
    assert user.email == "testuser@example.com"
