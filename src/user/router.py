from fastapi import APIRouter, Depends, HTTPException

from src.database import get_db
from src.auth.schemas.token_data import TokenData
from src.auth.dependencies import get_token_data
from src.user.schemas.user import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.service import UserService


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/get-user", response_model=UserSchema)
async def get_user(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """_summary_

    Args:
        token (TokenData, optional): _description_. Defaults to Depends(get_token_data).
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
    """
    try:
        async with db:  # Ensure proper context management
            return await UserService.get_user(db, token.id)
    except HTTPException as e:
        raise e
