from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import insert, delete, update
from src.hobby.models.category import Category
from src.hobby.schemas.category import CategorySchema, CategoryCreate
from src.hobby.models.hobby import Hobby
from src.hobby.schemas.hobby import HobbySchema, HobbyCreate, HobbyUpdate
from src.hobby.models.hobby import user_hobby_association


class HobbyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_hobby(self, hobby_id: int) -> Hobby | None:
        result = await self.db.execute(select(Hobby).where(Hobby.id == hobby_id))
        return result.scalar_one_or_none()

    async def create_hobby(self, hobby_data: HobbyCreate) -> Hobby:
        try:
            db_hobby = Hobby(**hobby_data.model_dump())
            self.db.add(db_hobby)
            await self.db.commit()
            await self.db.refresh(db_hobby)
            return db_hobby
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Hobby already exists or invalid category_id.") from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not create hobby.") from e

    async def update_hobby(self, hobby_id: int, hobby_data: HobbyUpdate) -> Hobby:
        db_hobby = await self.get_hobby(hobby_id)
        if not db_hobby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")

        update_values = hobby_data.model_dump(exclude_unset=True)
        if not update_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

        for key, value in update_values.items():
            setattr(db_hobby, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(db_hobby)
            return db_hobby
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Error updating hobby: {e.orig}") from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not update hobby.") from e

    async def delete_hobby(self, hobby_id: int) -> None:
        db_hobby = await self.get_hobby(hobby_id)
        if not db_hobby:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
        try:
            await self.db.delete(db_hobby)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            if isinstance(e, IntegrityError):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f"Cannot delete hobby. It might be in use by users.") from e
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not delete hobby.") from e

    async def get_user_hobbies(self, user_id: int) -> list[HobbySchema]:
        try:
            if user_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid user ID")
            result = await self.db.execute(
                select(Hobby)
                .join(user_hobby_association, Hobby.id == user_hobby_association.c.hobby_id)
                .where(user_hobby_association.c.user_id == user_id)
            )
            hobbies = result.scalars().all()
            return [HobbySchema.model_validate(hobby.__dict__) for hobby in hobbies]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def add_user_hobbies(self, user_id: int, hobby_ids: list[int]) -> dict:
        try:
            if user_id <= 0 or not hobby_ids or any(hobby_id <= 0 for hobby_id in hobby_ids):
                raise HTTPException(
                    status_code=400, detail="Invalid user or hobby IDs")
            await self.db.execute(
                insert(user_hobby_association).values(
                    [{"user_id": user_id, "hobby_id": hobby_id}
                        for hobby_id in hobby_ids]
                )
            )
            await self.db.commit()
            return {"detail": "Hobbies added successfully"}
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def delete_user_hobbies(self, user_id: int, hobby_ids: list[int]) -> dict:
        try:
            if user_id <= 0 or not hobby_ids or any(hobby_id <= 0 for hobby_id in hobby_ids):
                raise HTTPException(
                    status_code=400, detail="Invalid user or hobby IDs")
            result = await self.db.execute(
                delete(user_hobby_association).where(
                    (user_hobby_association.c.user_id == user_id) &
                    (user_hobby_association.c.hobby_id.in_(hobby_ids))
                )
            )
            await self.db.commit()
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=404, detail="No hobbies found for user")
            return {"detail": "Hobbies deleted successfully"}
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def edit_user_hobbies(self, user_id: int, hobby_ids: list[int]) -> dict:
        try:
            if user_id <= 0 or not hobby_ids or any(hobby_id <= 0 for hobby_id in hobby_ids):
                raise HTTPException(
                    status_code=400, detail="Invalid user or hobby IDs")

            existing_hobbies = await self.db.execute(
                select(user_hobby_association.c.hobby_id).where(
                    user_hobby_association.c.user_id == user_id
                )
            )
            existing_hobby_ids = set(existing_hobbies.scalars().all())

            hobbies_to_add = set(hobby_ids) - existing_hobby_ids
            hobbies_to_remove = existing_hobby_ids - set(hobby_ids)

            if hobbies_to_add:
                await self.db.execute(
                    insert(user_hobby_association).values(
                        [{"user_id": user_id, "hobby_id": hobby_id}
                            for hobby_id in hobbies_to_add]
                    )
                )

            if hobbies_to_remove:
                await self.db.execute(
                    delete(user_hobby_association).where(
                        (user_hobby_association.c.user_id == user_id) &
                        (user_hobby_association.c.hobby_id.in_(hobbies_to_remove))
                    )
                )

            await self.db.commit()
            return {"detail": "User hobbies updated successfully"}
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def search_hobbies(self, query: str) -> list[HobbySchema]:
        try:
            result = await self.db.execute(
                select(Hobby)
                .where(Hobby.name.ilike(f"%{query}%"))
            )
            hobbies = result.scalars().all()
            return [HobbySchema.model_validate(hobby.__dict__) for hobby in hobbies]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def create_category(self, name: str) -> CategorySchema:
        try:
            category = Category(name=name)
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(category)
            return CategorySchema.model_validate(category.__dict__)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category already exists") from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def get_all_categories(self) -> list[CategorySchema]:
        try:
            result = await self.db.execute(select(Category))
            categories = result.scalars().all()
            return [CategorySchema.model_validate(cat.__dict__) for cat in categories]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def get_category(self, category_id: int) -> CategorySchema:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return CategorySchema.model_validate(category.__dict__)

    async def update_category(self, category_id: int, name: str) -> CategorySchema:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        category.name = name
        try:
            await self.db.commit()
            await self.db.refresh(category)
            return CategorySchema.model_validate(category.__dict__)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category name already exists") from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def delete_category(self, category_id: int) -> None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        try:
            await self.db.delete(category)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
