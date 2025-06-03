from src.auth.service import AuthService
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
from sqlalchemy.orm import joinedload
from src.user.service import UserService
from src.hobby.models.hobby import user_hobby_association
from src.hobby.service import HobbyService
from src.user.schemas.user import UserCreate
from src.hobby.schemas.hobby import HobbyCreate
from src.hobby.schemas.category import CategoryCreate
from src.user.schemas.user_photo import UserPhotoSchema
from sqlalchemy import insert
from faker import Faker
import random
from sqlalchemy import select

fake = Faker()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Database reset complete")


async def insert_dummy_data(
    num_users: int = 10,
    num_categories: int = 3,
    hobbies_per_category: int = 5,
    hobbies_per_user: int = 3,
    num_messages: int = 20,
    num_likes: int = 10,
    photos_per_user: int = 2,
):
    async with async_session() as session:
        # Categories
        categories = []
        for _ in range(num_categories):
            category = Category(name=fake.unique.word().capitalize())
            session.add(category)
            categories.append(category)
        await session.flush()

        # Hobbies
        hobbies = []
        for category in categories:
            for _ in range(hobbies_per_category):
                hobby = Hobby(
                    name=fake.unique.word().capitalize(),
                    category_id=category.id
                )
                session.add(hobby)
                hobbies.append(hobby)
        await session.flush()

        # Users (use AuthService.register for hashing)
        users = []
        for _ in range(num_users):
            user_data = UserCreate(
                login=fake.unique.user_name(),
                email=fake.unique.email(),
                password="Password123#",
                password_confirmation="Password123#",
                phone_number=fake.phone_number()[:20],
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            await AuthService.register(session, user_data)
        await session.flush()
        users = (await session.execute(select(User))).scalars().all()

        # User Photos
        for user in users:
            for _ in range(photos_per_user):
                photo = UserPhoto(
                    user_id=user.id,
                    photo_url=fake.image_url()
                )
                session.add(photo)
        await session.flush()

        # User Hobbies
        # Avoid accessing ORM attributes after flush/commit; fetch IDs directly from DB
        hobby_ids = [row[0] for row in await session.execute(select(Hobby.id))]
        for user in users:
            selected_hobby_ids = random.sample(
                hobby_ids, min(hobbies_per_user, len(hobby_ids)))
            values = [{"user_id": user.id, "hobby_id": hobby_id}
                      for hobby_id in selected_hobby_ids]
            stmt = insert(user_hobby_association)
            await session.execute(stmt.values(values))

        # Matches (UserLiked)
        user_ids = [u.id for u in users]
        for _ in range(num_likes):
            liker, liked = random.sample(user_ids, 2)
            session.add(UserLiked(liker_id=liker, liked_id=liked))
        await session.flush()

        # Messages
        for _ in range(num_messages):
            sender, receiver = random.sample(user_ids, 2)
            message = Message(
                text=fake.sentence(),
                sender_id=sender,
                receiver_id=receiver,
                photo_url=fake.image_url() if random.random() < 0.3 else None
            )
            session.add(message)
        await session.commit()
        print(f"Inserted {num_users} users, {num_categories} categories, {len(hobbies)} hobbies, {num_messages} messages, {num_likes} likes, and photos.")
