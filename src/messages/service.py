from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from src.messages.models.message import Message
from src.messages.schemas.message import MessageSchema, MessageCreate, MessageUpdate
from src.user.models.user import User as UserModel  # For sender_id context


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_message(self, message_id: int, current_user_id: int) -> Message | None:
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        # Optional: Check if current_user is sender or receiver for authorization
        if message and (message.sender_id != current_user_id and message.receiver_id != current_user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not authorized to access this message")
        return message

    async def create_message(self, message_data: MessageCreate, sender_id: int) -> Message:
        db_message = Message(
            text=message_data.text,
            photo_url=message_data.photo_url,
            sender_id=sender_id,
            receiver_id=message_data.receiver_id
            # timestamp is usually handled by default in the model or DB
        )
        self.db.add(db_message)
        try:
            await self.db.commit()
            await self.db.refresh(db_message)
            return db_message
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not send message.") from e

    async def update_message(self, message_id: int, message_data: MessageUpdate, current_user_id: int) -> Message:
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        db_message = result.scalar_one_or_none()

        if not db_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        if db_message.sender_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not authorized to update this message")

        update_values = message_data.model_dump(exclude_unset=True)
        if not update_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

        for key, value in update_values.items():
            setattr(db_message, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(db_message)
            return db_message
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not update message.") from e

    async def delete_message(self, message_id: int, current_user_id: int) -> None:
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        db_message = result.scalar_one_or_none()

        if not db_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        # Only sender can delete, or implement soft delete / admin delete
        if db_message.sender_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not authorized to delete this message")

        try:
            await self.db.delete(db_message)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not delete message.") from e

    async def get_conversation(self, user1_id: int, user2_id: int, skip: int = 0, limit: int = 100) -> List[MessageSchema]:
        messages = await self.db.execute(
            select(Message)
            .where(
                ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
                ((Message.sender_id == user2_id) &
                 (Message.receiver_id == user1_id))
            )
            .order_by(Message.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return [MessageSchema.model_validate(msg) for msg in messages.scalars().all()]
