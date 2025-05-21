from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select
from sqlalchemy.orm import selectinload
from src.user.models.user import User
from src.user.schemas.user import UserSchema


class UserService:

    @staticmethod
    async def get_user(db: AsyncSession, id: int) -> UserSchema:
        user_query = (
            select(User)
            .where(User.id == id)
            .options(selectinload(User.photos))  # Eagerly load photos
        )
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserSchema.model_validate(user)
