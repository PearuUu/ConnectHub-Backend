from urllib import response
from xml.sax import default_parser_list
from fastapi import APIRouter, Depends, HTTPException, status, Response, Body

from src.database import get_db
from src.auth.schemas.token_data import TokenData
from src.auth.dependencies import get_token_data
from src.user.schemas.user import UserSchema, UserSearch, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.service import UserService
from src.user.schemas.user_photo import UserPhotoSchema

# Changed prefix to plural for consistency
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


# GET /users/me


@router.get("/me", response_model=UserSchema)
async def get_current_user(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to get the authenticated user's details.
    """
    try:
        async with db:
            return await UserService.get_user(db, token.id)
    except HTTPException as e:
        raise e

# PUT /users/me


@router.put("/me", response_model=UserSchema)
async def edit_current_user(
    user_data: UserUpdate,
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to edit the authenticated user's details.
    """
    return await UserService.edit_user(db, user_id=token.id, user_data=user_data)

# DELETE /users/me


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to delete the authenticated user.
    """
    await UserService.delete_user(db, token.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# POST /users/search


@router.post("/search", response_model=list[UserSchema])
async def search_users(
    user_data: UserSearch,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    """
    Endpoint to search for users by email or login.
    """
    return await UserService.search_user(db, user_data)

@router.get("/photo/{user_id}", response_model=list[UserPhotoSchema])
async def get_user_photos(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    return await UserService.get_user_photos(db, user_id)

@router.get("/me/photo", response_model=list[UserPhotoSchema])
async def get_current_user_photos(
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    return await UserService.get_user_photos(db, token.id)
# POST /users/me/photo


@router.post("/me/photo", response_model=UserPhotoSchema)
async def add_photo_to_profile(
    db: AsyncSession = Depends(get_db),
    photo_url: str = "",
    token: TokenData = Depends(get_token_data)
):
    """
    Endpoint to add a photo to the authenticated user's profile.
    """
    if photo_url == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Photo url not provided"
        )
    return await UserService.add_photo(db, photo_url, token.id)

# DELETE /users/me/photo/{photo_id}


@router.delete("/me/photo/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo_from_profile(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    """
    Endpoint to delete a user's photo by its ID.
    """
    await UserService.delete_photo(db, photo_id, token.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# PUT /users/me/profile-photo


@router.put("/me/profile-photo", response_model=UserSchema)
async def set_profile_photo(
    photo_id: int = Body(..., embed=True),
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Set the authenticated user's profile photo by photo_id.
    """
    return await UserService.set_profile_photo(db, user_id=token.id, photo_id=photo_id)

# DELETE /users/me/profile-photo


@router.delete("/me/profile-photo", response_model=UserSchema)
async def remove_profile_photo(
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove the authenticated user's profile photo.
    """
    return await UserService.remove_profile_photo(db, user_id=token.id)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    token: TokenData = Depends(get_token_data),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to get the user's details.
    """
    try:
        async with db:
            return await UserService.get_user(db, user_id)
    except HTTPException as e:
        raise e
    

