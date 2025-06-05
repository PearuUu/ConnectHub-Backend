from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from src.auth.dependencies import get_token_data, TokenData
from src.auth.schemas.register import RegisterResponse
from src.database import get_db
from src.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas.login import LoginRequest
from src.user.schemas.user import UserCreate
from src.auth.schemas.password import PasswordBase, PasswordChange

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
async def login(user: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Route for user login.
    """
    return await AuthService.login(db, user.login, user.password)


@router.post("/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    return await AuthService.register(db, user)


@router.put("/change-password", response_model=dict)
async def change_password(
    password_change: PasswordChange,
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to change the password of a user.
    """
    try:
        return await AuthService.change_password(db, token.id, password_change)
    except HTTPException as e:
        raise e


@router.put("/forgot-password", response_model=dict, status_code=status.HTTP_200_OK)
async def forgot_password(
    user_id: int,
    passwords: PasswordBase,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.forgot_password(db, user_id, passwords)


@router.get("/check-email", response_model=int)
async def check_email(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    user_id = await AuthService.check_email(db, email)
    return user_id
