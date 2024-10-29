#В этом файле содержатся зависимости и вспомогательные функции, такие как функции для аутентификации пользователей,
# создание JWT токенов и валидация токенов. Эти функции используются для защиты маршрутов и аутентификации.

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import Users
from datetime import datetime, timedelta, timezone
from app.config import settings, pwd_context


async def authenticate_user(email: str, password: str):
    query = select(Users).where(Users.email == email)
    async with AsyncSessionLocal() as session:
        result = await session.execute(query)
    user = result.scalar_one_or_none()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
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
        payload = jwt.decode(token.replace("Bearer ", ""), settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        query = select(Users).where(Users.email == email)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Users = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Вы не вошли в свой аккаунт.")
    return current_user