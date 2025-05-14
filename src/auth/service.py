from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import ExpiredSignatureError
from src.config import settings
from src.auth.schemas.token import TokenSchema
from src.user.schemas.user import UserCreate
from src.user.models.user import User
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select
from src.auth.schemas.register import RegisterResponse
from jose import jwt


pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
ALGORITHM = "HS256"


class AuthService:
    @staticmethod
    def _HashPassword(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def _VerifyPassword(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _GenerateToken(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, ALGORITHM)
        return token

    @staticmethod
    async def register(db: AsyncSession, user: UserCreate) -> RegisterResponse:
        hashed_password = AuthService._HashPassword(user.password)

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
        except exc.IntegrityError as e:
            await db.rollback()
            if "users_login_key" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Login already exists"
                )
            elif "users_email_key" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to register user"
                )
        except exc.SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {e}"
            )
        finally:
            if db.in_transaction():
                await db.rollback()

    @staticmethod
    async def login(db: AsyncSession, login: str, password: str) -> TokenSchema:
        user_query = select(User).where(User.login == login)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if not user or not AuthService._VerifyPassword(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = AuthService._GenerateToken({"id": str(user.id)})

        result = TokenSchema(
            access_token=token,
            token_type="bearer"
        )

        return result