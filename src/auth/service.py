from xml.dom.domreg import registered
from fastapi import HTTPException, status
from src.auth.schemas import password
from src.auth.schemas.password import PasswordChange
from src.config import settings
from src.auth.schemas.token import TokenSchema
from src.user.schemas.user import UserCreate, UserSchema
from src.user.models.user import User
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exc, select
from src.auth.schemas.register import RegisterResponse
from src.auth.utils.util import AuthUtil


pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
ALGORITHM = "HS256"


class AuthService:

    @staticmethod
    async def register(db: AsyncSession, user: UserCreate) -> RegisterResponse:
        hashed_password = AuthUtil.HashPassword(user.password)

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

        if not user or not AuthUtil.VerifyPassword(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = AuthUtil.GenerateToken({"id": str(user.id)})

        result = TokenSchema(
            access_token=token,
            token_type="bearer"
        )

        return result

    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, password_change: PasswordChange) -> dict:
        user_query = select(User).where(User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not AuthUtil.VerifyPassword(password_change.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        elif AuthUtil.VerifyPassword(password_change.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password can't be the same as the old password"
            )

        user.password = AuthUtil.HashPassword(password_change.password)
        try:
            await db.flush()
            await db.commit()
        except exc.SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update password: {e}"
            )

        return {"message": "Password updated successfully"}

    # TODO: Forgot password
    # TODO: Change password
    # TODO: Refresh token
    # TODO: Logout
