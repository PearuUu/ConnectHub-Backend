from src.database import engine, async_session
from src.models import Base
from src.auth.models.user import User
from src.auth.models.user_photo import UserPhoto


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 
        #await conn.run_sync(Base.metadata.tables["user_photos"].drop)
        #await conn.run_sync(Base.metadata.tables["users"].drop)
        #print(Base.metadata.tables)
        await conn.run_sync(Base.metadata.create_all)
        print("Database reset complete")
    
async def insertUser():
    async with async_session() as session:
        test_user = User(
            login="test_user",
            password="hashed_password_here",  # In production, hash this first!
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )

        session.add(test_user)
        try:
            await session.commit()
            print(f"Successfully added user: {test_user.login}")
            return test_user
        except Exception as e:
            await session.rollback()
            print(f"Error adding user: {e}")
            return None

