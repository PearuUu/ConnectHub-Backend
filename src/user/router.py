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


@router.get("/get", response_model=UserSchema)
async def get_user(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to get the authenticated user's details.
    """
    try:
        async with db:  # Ensure proper context management
            return await UserService.get_user(db, token.id)
    except HTTPException as e:
        raise e


@router.put("/edit", response_model=UserSchema)
async def edit_user(
    user_data: UserSchema,
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to edit a user's details.
    """
    user_data.id = token.id  # Ensure the ID matches the authenticated user
    return await UserService.edit_user(db, user_data)


@router.delete("/delete", status_code=204)
async def delete_user(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to delete the authenticated user.
    """
    await UserService.delete_user(db, token.id)
