# Эндпоинты для аутентификации и авторизации пользователей, такие как регистрация, логин, получение информации о пользователе и выход из системы.

from typing import Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, Request, Response, status

from app.dao import UserDAO
from app.dependencies import authenticate_user, create_access_token, get_current_user
from app.exceptions import EmailAlreadyUsed, EmailNotValid, InvalidCredentials
from app.schemas import UserBase, UserCreate, UserResponse
from app.utils import pwd_context

router = APIRouter()


@router.post("/register")
async def register(user: UserCreate) -> dict:
    try:
        valid = validate_email(user.email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError:
        raise EmailNotValid

    existing_user = await UserDAO.get_user_by_email(email)
    if existing_user:
        raise EmailAlreadyUsed

    hashed_password = pwd_context.hash(user.password)
    new_user = await UserDAO.create_user(email, hashed_password)
    return {"message": "Пользователь создан."}


@router.post("/login")
async def login(user_input: UserCreate, request: Request, response: Response) -> Optional[dict]:
    user = await authenticate_user(user_input.email, user_input.password)
    if not user:
        raise InvalidCredentials
    access_token = create_access_token({"sub": str(user.email)})

    # Set cookie in response
    # request.session.update({"token": access_token})
    response.set_cookie(
    key="session",
    value=access_token,
    httponly=True,
    secure=True,  # Set to True if using HTTPS
    samesite="None"  # Use "Lax" or "Strict" if not cross-origin
    )
    return {"token": access_token}


@router.get("/account")
async def get_account_details(
    current_user=Depends(get_current_user),
) -> Optional[UserBase]:
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> None:
    request.session.clear()
    return
