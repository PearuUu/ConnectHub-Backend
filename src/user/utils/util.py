from src.database import get_db
from src.user.models.user import User
from sqlalchemy import exc, select, delete, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

class UserUtils:
    @staticmethod
    async def get_db_user(db: AsyncSession, id: int) -> User:
        
        user_query = (
            select(User)
            .where(User.id == id)
            .options(selectinload(User.photos)) 
        )
        user = (await db.execute(user_query)).scalar_one_or_none()

        if not user:
            raise Exception(
                f"User with ID {id} not found."
            )
        
        return user
