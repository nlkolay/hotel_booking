# В этом файле содержатся зависимости и вспомогательные функции, такие как функции для аутентификации пользователей,
# создание JWT токенов и валидация токенов. Эти функции используются для защиты маршрутов и аутентификации.

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Request
from jose import JWTError, jwt
from pydantic import EmailStr
from sqlalchemy.future import select

from app.config import pwd_context, settings
from app.database import AsyncSessionLocal
from app.exceptions import InvalidCredentials, NotLoggedIn
from app.models import Users
from app.schemas import UserResponse


async def authenticate_user(email: str, password: str) -> UserResponse | None:
    query = select(Users).where(Users.email == email)
    async with AsyncSessionLocal() as session:
        result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# async def get_token(request: Request) -> Optional[Token]:
#     token: Token = request.session.get("token")
#     if token is None:
#         raise NotLoggedIn
#     return token


async def get_current_user(request: Request) -> Optional[UserResponse]:
    token: str = request.cookies.get("token")  # Use cookies instead of session
    if token is None:
        raise NotLoggedIn()

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: EmailStr = payload.get("sub")
        if email is None:
            raise InvalidCredentials()

        async with AsyncSessionLocal() as session:
            query = select(Users).where(Users.email == email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()

        if user is None:
            raise InvalidCredentials()

    except JWTError:
        raise InvalidCredentials()

    return user


async def get_current_user_session(request: Request) -> Optional[UserResponse]:
    # token: Token = await get_token(request)
    token: str = request.session.get("token_admin")
    if token is None:
        raise NotLoggedIn
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        email: EmailStr = payload.get("sub")
        if email is None:
            raise InvalidCredentials
        query = select(Users).where(Users.email == email)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise InvalidCredentials
    except JWTError:
        raise InvalidCredentials
    return user
