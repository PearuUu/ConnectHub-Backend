from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database import get_db
from src.auth.schemas.token_data import TokenData
from src.auth.dependencies import get_token_data
from src.user.schemas.user import UserSchema
from src.match.service import MatchService

router = APIRouter(
    prefix="/match",
    tags=["match"]
)


@router.post("/accept/{user_id}", status_code=status.HTTP_200_OK)
async def accept_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = MatchService(db)
    return await service.accept_user(liker_id=token.id, liked_id=user_id)


@router.post("/refuse/{user_id}", status_code=status.HTTP_200_OK)
async def refuse_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = MatchService(db)
    return await service.refuse_user(refuser_id=token.id, refused_id=user_id)


@router.get("/browse", response_model=List[UserSchema])
async def browse_users(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_token_data)
):
    service = MatchService(db)
    users = await service.browse_users(current_user_id=token.id, limit=limit)
    return [UserSchema.model_validate(user) for user in users]
