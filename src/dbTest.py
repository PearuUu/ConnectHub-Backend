from src.database import engine, async_session
from src.models import Base
from src.auth.Models.user import User

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("initialized")
    
async def insertUser():
    async with async_session() as session:
        new_user = User(login="test2", password="test123")
        print(new_user)
        await session.commit()

