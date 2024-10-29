#  Главный файл приложения FastAPI. Он создает экземпляр приложения, подключает роутеры и инициализирует
#  события запуска и завершения приложения. Теперь мы используем контекстный менеджер lifespan
#  для управления жизненным циклом приложения:

# to start app:
# uvicorn app.main:app --reload

from re import A
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from redis import asyncio as aioredis
from app.models import Bookings, Hotels, Rooms, Users
from app.routers import auth, hotels, rooms, bookings
from app.pages.router import router as router_pages
from app.images.router import router as router_images
from app.config import settings
from app.log import logger, handler
from app.admin.auth import authentication_backend


# Database setup
DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# Parallel with startup :
# async def get_cache():
#     while True:
#         print('start')
#         await asyncio.sleep(3)
#         print('end')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # Initiate redis
    redis = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}')
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Redis is ready.")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    #asyncio.create_task(get_cache())
    print('starting now')
    #
    yield
    #
    logger.info("Shutting down...")
    # Proper shutdown logic if needed (like closing connections)

app = FastAPI(
    title='Бронированией отелей Bronenosets',
    lifespan=lifespan
    )

origins = [
"http://localhost:3000",
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["GET", 'POST', 'OPTIONS', 'DELETE', 'PATCH', 'PUT'],  # Allow methods (GET, POST, etc.)
allow_headers=["Content-Type", 'Set-Cookie', 'Access-Control-Allow-Headers', 
               'Access-Control-Allow-Origins', 'Authorization'],  # Allow headers
)

# pics

app.mount('/static', StaticFiles(directory='app/static'), 'static')

# Ломает респонзы to front !!!!
# responses debug logger

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logger.info(f"Request: {request.method} {request.url}")
#     logger.debug(f"Request headers: {request.headers}")
#     logger.debug(f"Request body: {await request.body()}")

#     try:
#         response = await call_next(request)
#     except Exception as e:
#         logger.exception(f"Exception occurred: {e}")
#         return JSONResponse(content={"detail": str(e)}, status_code=500)

#     # Correctly log the response body
#     async for chunk in response.body_iterator:
#         logger.debug(f"Response chunk: {chunk.decode()}")

#     return response

#Backend routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

#Frontend routers
# app.include_router(router_pages)
# app.include_router(router_images)

admin = Admin(app, engine, authentication_backend=authentication_backend)


class UsersAdmin(ModelView, model=Users):
    can_delete = True
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_exclude_list = [Users.hashed_password]
    column_details_exclude_list = [Users.hashed_password]
    page_size = 100

class BookingsAdmin(ModelView, model=Bookings):
    can_delete = True
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-book"
    column_list = "__all__"
    page_size = 100

class HotelsAdmin(ModelView, model=Hotels):
    can_delete = True
    name = "Отель"
    name_plural = "Отели"
    icon = "fa-solid fa-hotel"
    column_list = "__all__"
    page_size = 100

class RoomsAdmin(ModelView, model=Rooms):
    can_delete = True
    name = "Комната"
    name_plural = "Комнаты"
    icon = "fa-solid fa-bed"
    column_list = "__all__"
    page_size = 100


admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)

# TODO 
# +front, 
# +cash, 
# test, 
# prod