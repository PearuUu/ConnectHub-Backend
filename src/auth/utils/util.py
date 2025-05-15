from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from src.config import settings
from fastapi import HTTPException, status
from src.auth.schemas.token_data import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
ALGORITHM = "HS256"


class AuthUtil:
    @staticmethod
    def HashPassword(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def VerifyPassword(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def GenerateToken(data: dict, expires_delta: timedelta = timedelta(minutes=60)):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, ALGORITHM)
        return token

    @staticmethod
    def TokenVerification(token: str) -> TokenData:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
            return TokenData(**payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
