from urllib import response
from xml.sax import default_parser_list
from fastapi import APIRouter, Depends, HTTPException, status

from src.database import get_db
from src.auth.schemas.token_data import TokenData
from src.auth.dependencies import get_token_data
from src.user.schemas.user import UserSchema, UserSearch
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.service import UserService
from src.user.schemas.user_photo import UserPhotoSchema


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


@router.post("/search", response_model=list[UserSchema])
async def search_user(
    user_data: UserSearch,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    """
    Endpoint to search for users by email or login.
    """
    return await UserService.search_user(db, user_data)


@router.post("/photo/add", response_model=UserPhotoSchema)
async def add_photo(
    db: AsyncSession = Depends(get_db),
    photo_url: str = "",
    token: TokenData = Depends(get_token_data)

):

    if photo_url == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Photo url not provided"
        )
    return await UserService.add_photo(db, photo_url, token.id)


@router.delete("/photo/delete/{photo_id}", status_code=204)
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    """
    Endpoint to delete a user's photo by its ID.
    """
    return await UserService.delete_photo(db, photo_id, token.id)
