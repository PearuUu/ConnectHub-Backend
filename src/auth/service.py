from src.user.schemas.user import UserCreate
from src.user.models.user import User
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc
from src.auth.schemas.register import RegisterResponse


pwd_context = CryptContext(schemes=["bcrypt"])


class AuthService:
    @staticmethod
    def _hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def register(db: AsyncSession, user: UserCreate) -> RegisterResponse:
        hashed_password = AuthService._hash_password(user.password)

        new_user = User(
            login=user.login,
            email=user.email,
            password=hashed_password,
            phone_number=user.phone_number,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        db.add(new_user)
        try:
            await db.flush()
            await db.commit()
            await db.refresh(new_user)

            response = RegisterResponse(
                user_id=new_user.id, email=new_user.email)

            return RegisterResponse.model_validate(response)
        except exc.SQLAlchemyError as e:
            raise e
        finally:
            if db.in_transaction():
                await db.rollback()
