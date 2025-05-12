from fastapi import APIRouter, Depends
from src.auth.schemas.register import RegisterResponse
from src.database import get_db
from src.auth.service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas.user import UserCreate  # Assuming this schema exists for user creation

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login")
async def login():
    """
    Placeholder route for user login.
    """
    return {"message": "Login endpoint"}

@router.post("/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    return await AuthService.register(db, user)