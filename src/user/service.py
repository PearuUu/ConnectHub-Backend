from xmlrpc.client import UNSUPPORTED_ENCODING
from fastapi import HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, insert, select, delete, or_
from sqlalchemy.orm import selectinload
from src.user.models.user import User
from src.user.schemas.user import UserSchema, UserSearch, UserUpdate
from src.user.schemas.user_photo import UserPhotoSchema
from src.user.utils.util import UserUtils
from src.user.models.user_photo import UserPhoto


class UserService:

    @staticmethod
    async def get_user(db: AsyncSession, id: int) -> UserSchema:
        user_query = (
            select(User)
            .where(User.id == id)
            .options(selectinload(User.profile_photo))
        )
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_dict = user.__dict__
        user_dict["profile_photo"] = (
            UserPhotoSchema.model_validate(user.profile_photo.__dict__)
            if user.profile_photo else None
        )

        return UserSchema.model_validate(user_dict)

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
    async def edit_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> UserSchema:
        try:
            user_query = select(User).where(User.id == user_id).options(selectinload(User.profile_photo))
            result = await db.execute(user_query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            update_values = user_data.model_dump(exclude_unset=True)
            for key, value in update_values.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)

            user_dict = user.__dict__
            user_dict["profile_photo"] = (
                UserPhotoSchema.model_validate(user.profile_photo.__dict__)
                if user.profile_photo else None
            )

            return UserSchema.model_validate(user_dict)
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

            filters = []
            for key, value in search_criteria.items():
                column = getattr(User, key)
                if isinstance(value, str):
                    filters.append(column.ilike(f"%{value}%"))
                else:
                    filters.append(column == value)

            user_query = select(User).where(*filters).options(selectinload(User.profile_photo))
            result = await db.execute(user_query)
            users = result.scalars().all()

            if not users:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No users found with the provided criteria"
                )
            
            user_dicts = [user.__dict__ for user in users]
            for i in range(len(user_dicts)):
                user_dicts[i]["profile_photo"] = (
                UserPhotoSchema.model_validate(users[i].profile_photo.__dict__)
                if users[i].profile_photo else None
                )

            return [UserSchema.model_validate(dict) for dict in user_dicts]
        except exc.SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while searching for users"
            ) from e

    @staticmethod
    async def get_user_photos(db: AsyncSession, user_id: int) -> list[UserPhotoSchema]:
        try:
            query = select(UserPhoto).where(UserPhoto.user_id == user_id)
            result = await db.execute(query)
            photos = result.scalars().all()
            if not photos:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No photos found for this user"
                )
            return [UserPhotoSchema.model_validate(photo.__dict__) for photo in photos]
        except exc.SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching photos"
            ) from e

    @staticmethod
    async def add_photo(db: AsyncSession, photo_url: str, user_id: int) -> UserPhotoSchema:
        try:
            user_photo = UserPhoto(
                user_id=user_id,
                photo_url=photo_url
            )
            db.add(user_photo)
            await db.flush()
            await db.commit()
            await db.refresh(user_photo)

            result = UserPhotoSchema(
                id=user_photo.id,
                user_id=user_photo.user_id,
                photo_url=user_photo.photo_url
            )

            return UserPhotoSchema.model_validate(result)

        except exc.SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while adding the photo"
            ) from e

    @staticmethod
    async def delete_photo(db: AsyncSession, photo_id: int, user_id: int):
        try:
            query = delete(UserPhoto).where(
                (UserPhoto.id == photo_id) and (UserPhoto.user_id == user_id))
            result = await db.execute(query)
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
                detail="An error occurred while adding the photo"
            ) from e

    @staticmethod
    async def set_profile_photo(db: AsyncSession, user_id: int, photo_id: int) -> UserSchema:
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        # Check that the photo belongs to the user
        photo_query = select(UserPhoto).where(
            UserPhoto.id == photo_id, UserPhoto.user_id == user_id)
        photo_result = await db.execute(photo_query)
        photo = photo_result.scalar_one_or_none()
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found or does not belong to user"
            )
        user.profile_photo_id = photo_id
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return await UserService.get_user(db, user_id)

    @staticmethod
    async def remove_profile_photo(db: AsyncSession, user_id: int) -> UserSchema:
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user.profile_photo_id = None
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return await UserService.get_user(db, user_id)
