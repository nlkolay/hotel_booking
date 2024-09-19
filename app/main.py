from fastapi import FastAPI
from app.routers import auth, hotels, rooms, bookings
from app.database import Base, engine

app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
