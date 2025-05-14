import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.messages.models.message import Message


async def test_message_model(db: AsyncSession):
    message = Message(
        text="Hello, World!",
        sender_id=1,
        receiver_id=2
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    assert message.id is not None
    assert message.text == "Hello, World!"
    assert message.sender_id == 1
    assert message.receiver_id == 2
