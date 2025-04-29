from src.database import engine, async_session

from src.models import Base, User

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
async def insertUser():
    async with async_session() as session:
        new_user = User(username="test2", password="test123")
        print(new_user)
        session.add(new_user)
        await session.commit()
        print("comitted")