# Этот файл занимается настройкой соединения с базой данных. Он создает объект сессии и базу данных.
# Здесь мы используем SQLAlchemy для работы с базой данных PostgreSQL.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
from app.config import settings

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session