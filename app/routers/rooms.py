# Эндпоинты для работы с информацией о комнатах в отелях.

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import HotelDAO
from app.dependencies import get_db
from app.schemas import RoomResponse
from typing import List

router = APIRouter()

@router.get("/{hotel_id}/rooms", response_model=List[RoomResponse])
async def list_rooms(hotel_id: int, db: AsyncSession = Depends(get_db)):
    hotel_dao = HotelDAO(db)
    rooms = await hotel_dao.get_rooms_by_hotel_id(hotel_id)
    return rooms
