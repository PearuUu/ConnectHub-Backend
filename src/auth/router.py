from fastapi import APIRouter, Depends, HTTPException
from src.auth.schemas.register import RegisterResponse
from src.database import get_db
from src.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas.login import LoginRequest
from src.user.schemas.user import UserCreate
from src.auth.schemas.password import PasswordChange

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
    user_id: int,
    password_change: PasswordChange,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to change the password of a user.
    """
    try:
        return await AuthService.change_password(db, user_id, password_change)
    except HTTPException as e:
        raise e
