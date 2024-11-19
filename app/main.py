#  Главный файл приложения FastAPI. Он создает экземпляр приложения, подключает роутеры и инициализирует
#  события запуска и завершения приложения. Теперь мы используем контекстный менеджер lifespan
#  для управления жизненным циклом приложения:

# to start app:
# uvicorn app.main:app --reload

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from prometheus_fastapi_instrumentator import Instrumentator

# from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.config import settings
from app.database import engine
from app.log import handler, logger
from app.pages.router import router as router_pages
from app.routers import auth, bookings, hotels, prometheus, rooms, utils

# For logging mgmt (ru 403):
# import sentry_sdk
# sentry_sdk.init(
#     dsn=settings.SENTRY_DSN,
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )

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
    yield
    logger.info("Shutting down...")
    # Proper shutdown logic if needed (like closing connections)


app = FastAPI(title="Бронирование отелей Bronenosets", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://hotel-booking-frontend-pt56.onrender.com"
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

# For user session control:

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Responses debug logger:
# WARN: If commented, prometheus metrics will show constant rate of 500...

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request body: {await request.body()}")
    start_time  = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Exception occurred: {e}")
        return JSONResponse(content={"detail": str(e)}, status_code=500)
    process_time =  time.time() - start_time
    logger.debug(
        f"Request: {request.method} {request.url}",
        extra={
        "process_time": round(process_time, 4)
        }
        )
    # async for chunk in response.body_iterator:
    #     logger.debug(f"Response chunk: {chunk.decode()}") Ломает респонзы!!!

    return response

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)

# Backend routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

app.include_router(utils.router)
app.include_router(prometheus.router)

# Frontend routers
# app.include_router(router_pages)

# app = VersionedFastAPI(app,
#     version_format='{major}',
#     prefix_format='/v{major}',
#     # description='Greet users with a nice message',
#     # middleware=[
#     #     Middleware(SessionMiddleware, secret_key='mysecretkey')
#     # ]
# )

admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)

# pics
app.mount("/static", StaticFiles(directory="app/static"), "static")

# TODO
# +front,
# +cash,
# +test,
# prod
