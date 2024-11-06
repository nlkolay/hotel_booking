#  Главный файл приложения FastAPI. Он создает экземпляр приложения, подключает роутеры и инициализирует
#  события запуска и завершения приложения. Теперь мы используем контекстный менеджер lifespan
#  для управления жизненным циклом приложения:

# to start app:
# uvicorn app.main:app --reload

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.config import settings
from app.database import engine
from app.log import handler, logger
from app.pages.router import router as router_pages
from app.images.router import router as router_images
from app.routers import auth, bookings, hotels, rooms

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
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Redis is ready.")
    # Create database tables
    # async with AsyncSessionLocal() as session:
    #     await session.run_sync(Base.metadata.create_all)
    # asyncio.create_task(get_cache())
    print("starting now")
    #
    yield
    #
    logger.info("Shutting down...")
    # Proper shutdown logic if needed (like closing connections)


app = FastAPI(title="Бронированией отелей Bronenosets", lifespan=lifespan)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
        "DELETE",
        "PATCH",
        "PUT",
    ],  # Allow methods (GET, POST, etc.)
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origins",
        "Authorization",
    ],  # Allow headers
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# pics

app.mount("/static", StaticFiles(directory="app/static"), "static")

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

# Backend routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

# Frontend routers
# app.include_router(router_pages)
# app.include_router(router_images)

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)

# TODO
# +front,
# +cash,
# +test,
# prod
