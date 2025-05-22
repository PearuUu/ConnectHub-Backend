from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select, delete, or_
from sqlalchemy.orm import selectinload
from src.user.models.user import User
from src.user.schemas.user import UserSchema, UserSearch


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

    @staticmethod
    async def delete_user(db: AsyncSession, id: int) -> int:
        try:
            delete_query = delete(User).where(User.id == id)
            result = await db.execute(delete_query)
            await db.commit()
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return result.rowcount
        except exc.SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the user"
            ) from e

    @staticmethod
    async def edit_user(db: AsyncSession, user_data: UserSchema) -> UserSchema:
        try:
            user_query = select(User).where(User.id == user_data.id)
            result = await db.execute(user_query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            for key, value in user_data.model_dump(exclude={"id"}, exclude_unset=True).items():
                if hasattr(user, key):
                    setattr(user, key, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            return UserSchema.model_validate(user)
        except exc.SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while editing the user"
            ) from e

    @staticmethod
    async def search_user(db: AsyncSession, user_data: UserSearch) -> list[UserSchema]:
        try:
            search_criteria = user_data.model_dump(exclude_unset=True)

            if not search_criteria:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one search criterion must be provided"
                )

            filters = [getattr(User, key) == value for key,
                       value in search_criteria.items()]
            user_query = select(User).where(*filters)
            result = await db.execute(user_query)
            users = result.scalars().all()

            if not users:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No users found with the provided criteria"
                )

            return [UserSchema.model_validate(user) for user in users]
        except exc.SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while searching for users"
            ) from e
