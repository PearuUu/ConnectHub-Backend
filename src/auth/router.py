from fastapi import APIRouter, Depends
from src.auth.schemas.register import RegisterResponse
from src.database import get_db
from src.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession # Import LoginRequest schema
from src.auth.schemas.login import LoginRequest
from src.user.schemas.user import UserCreate

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
