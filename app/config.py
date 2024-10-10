# Этот файл содержит настройки проекта и валидацию переменных окружения с использованием Pydantic. Он обеспечивает централизованное место для управления конфигурацией проекта.

from pydantic import Field, EmailStr
from typing import Optional
from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES", gt=0)
    DB_SERVER: Optional[str] = Field(None, env="DB_SERVER")
    DB_PORT: Optional[int] = Field(None, env="DB_PORT")
    DB_USER: Optional[str] = Field(None, env="DB_USER")
    DB_PASSWORD: Optional[str] = Field(None, env="DB_PASSWORD")

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    REDIS_HOST: str
    REDIS_PORT: int

class Config:
    env_file = ".env"

settings = Settings()