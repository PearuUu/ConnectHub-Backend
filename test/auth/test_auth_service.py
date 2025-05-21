import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.service import AuthService
from src.auth.schemas.password import PasswordChange
from src.auth.schemas.token import TokenSchema
from src.user.schemas.user import UserCreate
from src.auth.schemas.register import RegisterResponse
from test.models import *


@pytest.mark.asyncio
async def test_register_success():
    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(
        login="testuser",
        email="test@example.com",
        password="Password123#",
        password_confirmation="Password123#",
        phone_number="1234567890",
        first_name="Test",
        last_name="User"
    )
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    # Mock db.refresh to assign an id to the new user
    def mock_refresh(user):
        user.id = 1

    db.refresh = AsyncMock(side_effect=mock_refresh)

    response = await AuthService.register(db, user_data)

    assert isinstance(response, RegisterResponse)
    assert response.email == user_data.email
    assert response.user_id == 1
    db.add.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email():
    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(
        login="testuser",
        email="duplicate@example.com",
        password="Password123#",  # Updated to meet validation requirements
        password_confirmation="Password123#",  # Updated to match the password
        phone_number="1234567890",
        first_name="Test",
        last_name="User"
    )
    db.flush = AsyncMock(side_effect=HTTPException(
        status_code=400, detail="Email already exists"))
    db.rollback = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.register(db, user_data)

    assert exc_info.value.status_code == 400
    assert "Email already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_success():
    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(
        login="testuser",
        email="test@example.com",
        password="Password123#",
        password_confirmation="Password123#",
        phone_number="1234567890",
        first_name="Test",
        last_name="User"
    )

    # Use the register method to add the user
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    def mock_refresh(user):
        user.id = 1

    db.refresh = AsyncMock(side_effect=mock_refresh)
    await AuthService.register(db, user_data)

    with patch("src.auth.utils.util.AuthUtil.VerifyPassword", return_value=True):
        with patch("src.auth.utils.util.AuthUtil.GenerateToken", return_value="test_token"):
            token = await AuthService.login(db, user_data.login, user_data.password)

    assert isinstance(token, TokenSchema)
    assert token.access_token == "test_token"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=AsyncMock(
        scalar_one_or_none=AsyncMock(return_value=None)))

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.login(db, "invaliduser", "wrongpassword")

    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_change_password_success():
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1, password="hashed_password")
    db.execute = AsyncMock(return_value=AsyncMock(
        scalar_one_or_none=AsyncMock(return_value=user)))
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    password_change = PasswordChange(
        current_password="old_password", password="new_password")

    with patch("src.auth.utils.util.AuthUtil.VerifyPassword", AsyncMock(side_effect=[True, False])):
        with patch("src.auth.utils.util.AuthUtil.HashPassword", AsyncMock(return_value="new_hashed_password")):
            response = await AuthService.change_password(db, 1, password_change)

    assert response["message"] == "Password updated successfully"
    assert user.password == "new_hashed_password"


@pytest.mark.asyncio
async def test_change_password_incorrect_current_password():
    db = AsyncMock(spec=AsyncSession)
    user = User(id=1, password="hashed_password")
    db.execute = AsyncMock(return_value=AsyncMock(
        scalar_one_or_none=AsyncMock(return_value=user)))

    password_change = PasswordChange(
        current_password="wrong_password", password="new_password")

    with patch("src.auth.utils.util.AuthUtil.VerifyPassword", AsyncMock(return_value=False)):
        with pytest.raises(HTTPException) as exc_info:
            await AuthService.change_password(db, 1, password_change)

    assert exc_info.value.status_code == 401
    assert "Current password is incorrect" in exc_info.value.detail


@pytest.mark.asyncio
async def test_register_multiple_users():
    db = AsyncMock(spec=AsyncSession)
    users_data = [
        UserCreate(
            login=f"user{i}",
            email=f"user{i}@example.com",
            password="Password123#",
            password_confirmation="Password123#",
            phone_number=f"123456789{i}",
            first_name=f"First{i}",
            last_name=f"Last{i}"
        )
        for i in range(1, 4)  # Create data for 3 users
    ]

    db.flush = AsyncMock()
    db.commit = AsyncMock()

    # Create a mapping to assign unique IDs
    user_mapping = {}

    def mock_refresh(user):
        if user not in user_mapping:
            user_mapping[user] = len(user_mapping) + 1
        user.id = user_mapping[user]

    db.refresh = AsyncMock(side_effect=mock_refresh)

    for user_data in users_data:
        response = await AuthService.register(db, user_data)
        assert isinstance(response, RegisterResponse)
        assert response.email == user_data.email
        assert response.user_id == int(user_data.login[-1])
