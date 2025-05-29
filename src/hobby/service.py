from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import insert, delete
from src.hobby.models.hobby import Hobby
from src.hobby.schemas.hobby import HobbySchema
from src.hobby.models.hobby import user_hobby_association


class HobbyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_hobby(self, hobby_id: int) -> Hobby:
        try:
            if hobby_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid hobby ID")
            result = await self.db.execute(select(Hobby).where(Hobby.id == hobby_id))
            hobby = result.scalar_one_or_none()
            if not hobby:
                raise HTTPException(status_code=404, detail="Hobby not found")
            return hobby
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def create_hobby(self, hobby_data: HobbySchema) -> Hobby:
        try:
            hobby = Hobby(**hobby_data.model_dump())
            hobby.id = None
            self.db.add(hobby)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(hobby)
            return hobby
        except IntegrityError as e:
            if 'UniqueViolationError' in str(e.orig):
                raise HTTPException(
                    status_code=400, detail="Hobby name must be unique")
            else:
                raise HTTPException(
                    status_code=400, detail=f"Integrity error occurred: {e}")
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def update_hobby(self, hobby_id: int, hobby_data: HobbySchema) -> Hobby:
        try:
            if hobby_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid hobby ID")
            hobby = await self.get_hobby(hobby_id)
            for key, value in hobby_data.dict().items():
                if key != "id":  # Ensure the ID field is not updated
                    setattr(hobby, key, value)
            await self.db.commit()
            await self.db.refresh(hobby)
            return hobby
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

    async def delete_hobby(self, hobby_id: int) -> dict:
        try:
            if hobby_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid hobby ID")
            hobby = await self.get_hobby(hobby_id)
            await self.db.delete(hobby)
            await self.db.commit()
            return {"detail": "Hobby deleted successfully"}
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {e}")

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

            # Fetch existing hobbies for the user
            existing_hobbies = await self.db.execute(
                select(user_hobby_association.c.hobby_id).where(
                    user_hobby_association.c.user_id == user_id
                )
            )
            existing_hobby_ids = set(existing_hobbies.scalars().all())

            # Determine hobbies to add and remove
            hobbies_to_add = set(hobby_ids) - existing_hobby_ids
            hobbies_to_remove = existing_hobby_ids - set(hobby_ids)

            # Add new hobbies
            if hobbies_to_add:
                await self.db.execute(
                    insert(user_hobby_association).values(
                        [{"user_id": user_id, "hobby_id": hobby_id}
                            for hobby_id in hobbies_to_add]
                    )
                )

            # Remove old hobbies
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
