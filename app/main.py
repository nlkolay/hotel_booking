#  Главный файл приложения FastAPI. Он создает экземпляр приложения, подключает роутеры и инициализирует
#  события запуска и завершения приложения. Теперь мы используем контекстный менеджер lifespan
#  для управления жизненным циклом приложения:

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from app.routers import auth, hotels, rooms, bookings
from app.pages.router import router as router_pages
from app.config import settings
import logging
from fastapi.middleware.cors import CORSMiddleware


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a handler (e.g., to write logs to a file)
handler = logging.FileHandler("my_app.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Add the handler to the logger
logger.addHandler(handler)

# Database setup
DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("Shutting down...")
    # Proper shutdown logic if needed (like closing connections)

app = FastAPI(lifespan=lifespan)

origins = [
"http://localhost:3000",
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
allow_headers=["*"],  # Allow all headers
)

# Ломает респонзы!!!!

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
app.include_router(router_pages)

# TODO front, cash, test, prod

# start app:
# uvicorn app.main:app --reload