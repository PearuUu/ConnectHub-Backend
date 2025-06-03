from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, not_, exists
from src.user.models.user import User
from src.match.models.userLiked import UserLiked
from src.hobby.models.hobby import user_hobby_association
import random


class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def accept_user(self, liker_id: int, liked_id: int):
        if liker_id == liked_id:
            raise HTTPException(status_code=400, detail="Cannot like yourself")
        # Check if already liked
        result = await self.db.execute(
            select(UserLiked).where(
                (UserLiked.liker_id == liker_id) & (
                    UserLiked.liked_id == liked_id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already liked")
        user_liked = UserLiked(liker_id=liker_id, liked_id=liked_id)
        self.db.add(user_liked)
        await self.db.commit()
        return {"detail": "User liked"}

    async def refuse_user(self, refuser_id: int, refused_id: int):
        # For now, refusing is just not liking, but we can add a "refused" table if needed.
        # Here, we just return success (could be extended).
        if refuser_id == refused_id:
            raise HTTPException(
                status_code=400, detail="Cannot refuse yourself")
        return {"detail": "User refused"}

    async def browse_users(self, current_user_id: int, limit: int = 10):
        # Get current user's hobbies
        hobbies_result = await self.db.execute(
            select(user_hobby_association.c.hobby_id).where(
                user_hobby_association.c.user_id == current_user_id
            )
        )
        user_hobby_ids = set(hobbies_result.scalars().all())

        # Subquery: users already liked by current user
        liked_subq = select(UserLiked.liked_id).where(
            UserLiked.liker_id == current_user_id)
        # Exclude self, already liked
        user_query = (
            select(User)
            .where(
                (User.id != current_user_id) &
                (~User.id.in_(liked_subq))
            )
        )
        # Optionally: filter users with at least one shared hobby
        if user_hobby_ids:
            user_query = user_query.where(
                exists().where(
                    (user_hobby_association.c.user_id == User.id) &
                    (user_hobby_association.c.hobby_id.in_(user_hobby_ids))
                )
            )
        user_query = user_query.order_by(func.random()).limit(limit)
        result = await self.db.execute(user_query)
        users = result.scalars().all()
        # Optionally, shuffle for randomness
        random.shuffle(users)
        return users
