import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import AuthService
from src.user.models.user import User
from src.user.schemas.user import UserCreate
from src.auth.schemas.token import TokenSchema
from sqlalchemy import select


@pytest.fixture
async def test_user(db: AsyncSession):
    user = User(
        login="testuser",
        email="testuser@example.com",
        password=AuthService._HashPassword("Testuser1!"),
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def test_register_user(db: AsyncSession):
    user_data = UserCreate(
        login="newuser",
        email="newuser@example.com",
        password="Password123!",
        password_confirmation="Password123!",
        first_name="New",
        last_name="User"
    )
    response = await AuthService.register(db, user_data)
    assert response.user_id is not None
    assert response.email == user_data.email


async def test_login_user(db: AsyncSession, test_user: User):
    token = await AuthService.login(db, test_user.login, "Testuser1!")
    assert isinstance(token, TokenSchema)
    assert token.token_type == "bearer"


async def test_login_invalid_credentials(db: AsyncSession):
    with pytest.raises(Exception):
        await AuthService.login(db, "invaliduser", "wrongpassword")
