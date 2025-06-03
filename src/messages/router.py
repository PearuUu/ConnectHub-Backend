from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database import get_db  # Changed from get_db_session to get_db
from src.messages.schemas.message import MessageSchema, MessageCreate, MessageUpdate
from src.messages.service import MessageService
from src.auth.schemas.token_data import TokenData  # Added
from src.auth.dependencies import get_token_data  # Added
# For type hint if needed, though token.id is primary
from src.user.models.user import User as UserModel

router = APIRouter(
    prefix="/messages",
    tags=["messages"]
)


@router.post("/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
async def send_new_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    # Changed from current_user to token
    token: TokenData = Depends(get_token_data)
):
    service = MessageService(db)
    if token.id == message_data.receiver_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot send message to yourself.")
    return await service.create_message(message_data=message_data, sender_id=token.id)


@router.get("/{message_id}", response_model=MessageSchema)
async def get_message_by_id(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    # Changed from current_user to token
    token: TokenData = Depends(get_token_data)
):
    service = MessageService(db)
    message = await service.get_message(message_id=message_id, current_user_id=token.id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Message not found or not authorized")
    return MessageSchema.model_validate(message)


@router.put("/{message_id}", response_model=MessageSchema)
async def update_sent_message(
    message_id: int,
    message_data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    # Changed from current_user to token
    token: TokenData = Depends(get_token_data)
):
    service = MessageService(db)
    return await service.update_message(message_id=message_id, message_data=message_data, current_user_id=token.id)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sent_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    # Changed from current_user to token
    token: TokenData = Depends(get_token_data)
):
    service = MessageService(db)
    await service.delete_message(message_id=message_id, current_user_id=token.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/conversation/{user_id}", response_model=List[MessageSchema])
async def get_user_conversation(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    # Changed from current_user to token
    token: TokenData = Depends(get_token_data)
):
    service = MessageService(db)
    if token.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot get conversation with yourself using this endpoint.")
    return await service.get_conversation(user1_id=token.id, user2_id=user_id, skip=skip, limit=limit)
