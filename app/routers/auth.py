# Эндпоинты для аутентификации и авторизации пользователей, такие как регистрация, логин, получение информации о пользователе и выход из системы.

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.dependencies import authenticate_user, create_access_token, get_db, get_current_user
from app.dao import UserDAO
from email_validator import validate_email, EmailNotValidError
from app.utils import pwd_context

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        valid = validate_email(user.email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email")

    user_dao = UserDAO(db)
    existing_user = await user_dao.get_user_by_email(email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = await user_dao.create_user(email, hashed_password)
    #access_token = create_access_token(data={"sub": new_user.email})
    return #{"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db), response: Response = None):
    user = await authenticate_user(db, user.email, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": user.email})

#Set cookie in response
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/account", response_model=UserResponse)
async def get_account_details(current_user = Depends(get_current_user)):
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return