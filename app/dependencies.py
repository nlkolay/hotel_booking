#В этом файле содержатся зависимости и вспомогательные функции, такие как функции для аутентификации пользователей,
# создание JWT токенов и валидация токенов. Эти функции используются для защиты маршрутов и аутентификации.

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from app.config import settings
from app.dao import UserDAO
from app.models import Users
from app.schemas import UserResponse
from app.utils import pwd_context


# Load environment variables from .env file
load_dotenv()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def authenticate_user(
        db: AsyncSession,
        email: EmailStr, 
        password: str
        ) -> Optional[UserResponse]:
    user_dao = UserDAO(db)
    user = await user_dao.get_user_by_email(email)
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
        request: Request, 
        db: AsyncSession
        ) -> UserResponse:
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пожалуйста, войдите в аккаунт.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные данные пользователя.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.replace("Bearer ", ""), SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("sub")
        if email is None:
            raise credentials_exception
        user_dao = UserDAO(db)
        user = await user_dao.get_user_by_email(email)
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Users = Depends(get_current_user)
        ) -> UserResponse:
    if not current_user:
        raise HTTPException(status_code=400, detail="Вы не вошли в свой аккаунт.")
    return current_user