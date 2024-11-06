# Этот файл занимается настройкой соединения с базой данных.
# Он создает объект сессии и базу данных.
# Здесь мы готовим SQLAlchemy для работы с базой данных PostgreSQL.
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
    # Define the parameters for the database connection,
    # using NullPool for connection pooling
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


@classmethod
async def session():
    async with AsyncSessionLocal() as session:
        yield session
