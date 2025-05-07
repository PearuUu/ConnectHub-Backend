from src.database import engine, async_session
from src.models import Base
from src.user.models.user import User
from src.user.models.user_photo import UserPhoto
from src.hobby.models.hobby import Hobby
from src.hobby.models.category import Category
from src.match.models.userLiked import UserLiked
from src.messages.models.message import Message
from sqlalchemy.sql import text
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, joinedload


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

async def insert_dummy_data():
    async with async_session() as session:
        try:
            # Insert dummy data for User
            user1 = User(
                login="user1",
                password="hashed_password1",
                email="user1@example.com",
                first_name="John",
                last_name="Doe",
                phone_number="1234567890"
            )
            user2 = User(
                login="user2",
                password="hashed_password2",
                email="user2@example.com",
                first_name="Jane",
                last_name="Smith",
                phone_number="0987654321"
            )
            session.add_all([user1, user2])
            await session.flush()  # Ensure IDs are available for related models

            # Insert dummy data for UserPhoto
            photo1 = UserPhoto(user_id=user1.id, photo_url="http://example.com/photo1.jpg")
            photo2 = UserPhoto(user_id=user2.id, photo_url="http://example.com/photo2.jpg")
            session.add_all([photo1, photo2])

            # Insert dummy data for Category
            category = Category(name="Sports")
            session.add(category)
            await session.flush()  # Ensure category ID is available for Hobby

            # Insert dummy data for Hobby
            hobby = Hobby(name="Football", category_id=category.id)
            session.add(hobby)

            # Insert dummy data for UserLiked
            user_liked = UserLiked(liker_id=user1.id, liked_id=user2.id)
            session.add(user_liked)

            # Insert dummy data for Message
            message = Message(
                text="Hello, how are you?",
                photo_url=None,
                sender_id=user1.id,
                receiver_id=user2.id
            )
            session.add(message)

            await session.commit()
            print("Dummy data inserted successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error inserting dummy data: {e}")

async def select_and_print_data():
    async with async_session() as session:
        try:
            # Fetch and print all users
            users = await session.execute(text("SELECT * FROM users"))
            print("Users:")
            for row in users.fetchall():
                print(row)

            # Fetch and print all user photos
            photos = await session.execute(text("SELECT * FROM user_photos"))
            print("User Photos:")
            for row in photos.fetchall():
                print(row)

            # Fetch and print all categories
            categories = await session.execute(text("SELECT * FROM categories"))
            print("Categories:")
            for row in categories.fetchall():
                print(row)

            # Fetch and print all hobbies
            hobbies = await session.execute(text("SELECT * FROM hobbies"))
            print("Hobbies:")
            for row in hobbies.fetchall():
                print(row)

            # Fetch and print all user likes
            user_likes = await session.execute(text("SELECT * FROM user_likes"))
            print("User Likes:")
            for row in user_likes.fetchall():
                print(row)

            # Fetch and print all messages
            messages = await session.execute(text("SELECT * FROM messages"))
            print("Messages:")
            for row in messages.fetchall():
                print(row)
        except Exception as e:
            print(f"Error selecting data: {e}")

async def get_user_with_messages(user_id: int):
    async with async_session() as session:
        try:
            # Fetch the user object with related messages
            result = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(
                    joinedload(User.sent_messages),  # Eagerly load sent messages
                    joinedload(User.received_messages)  # Eagerly load received messages
                )
            )
            user = result.scalars().first()

            if user:
                print(f"User: {user}")
                print("Sent Messages:")
                for message in user.sent_messages:
                    print(message)
                print("Received Messages:")
                for message in user.received_messages:
                    print(message)
            else:
                print(f"No user found with ID {user_id}")
        except Exception as e:
            print(f"Error fetching user: {e}")

