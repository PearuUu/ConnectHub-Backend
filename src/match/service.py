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
        if refuser_id == refused_id:
            raise HTTPException(
                status_code=400, detail="Cannot refuse yourself")
        return {"detail": "User refused"}

    async def browse_users(self, current_user_id: int, limit: int = 10):
        hobbies_result = await self.db.execute(
            select(user_hobby_association.c.hobby_id).where(
                user_hobby_association.c.user_id == current_user_id
            )
        )
        user_hobby_ids = set(hobbies_result.scalars().all())

        liked_subq = select(UserLiked.liked_id).where(
            UserLiked.liker_id == current_user_id)
        user_query = (
            select(User)
            .where(
                (User.id != current_user_id) &
                (~User.id.in_(liked_subq))
            )
        )
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
        random.shuffle(users)
        return users

    async def get_pending_likes(self, user_id: int, limit: int = 10, isIncoming = False):
        liked_subq = select(UserLiked.liker_id).where(
            UserLiked.liked_id == user_id) if isIncoming else select(UserLiked.liked_id).where(
            UserLiked.liker_id == user_id)
        
        user_query = (
            select(User)
            .where(User.id.in_(liked_subq))
            .limit(limit)
        )

        result = await self.db.execute(user_query)
        users = result.scalars().all()
        matches = await self.get_matches(user_id)
        
        return [user for user in users if user not in matches]

    async def get_matches(self, user_id: int, limit: int = 10):
        liked_subq = select(UserLiked.liked_id).where(
            UserLiked.liker_id == user_id)
        liked_by_subq = select(UserLiked.liker_id).where(
            UserLiked.liked_id == user_id)
        user_query = (
            select(User)
            .where(
                User.id.in_(liked_subq),
                User.id.in_(liked_by_subq)
            )
            .limit(limit)
        )
        result = await self.db.execute(user_query)
        users = result.scalars().all()
        return users

    async def undo_like(self, liker_id: int, liked_id: int):
        result = await self.db.execute(
            select(UserLiked).where(
                (UserLiked.liker_id == liker_id) & (
                    UserLiked.liked_id == liked_id)
            )
        )

        user_liked = result.scalar_one_or_none()
        if not user_liked:
            raise HTTPException(status_code=404, detail="Like not found")
        await self.db.delete(user_liked)
        await self.db.commit()
        return {"detail": "Like undone"}
