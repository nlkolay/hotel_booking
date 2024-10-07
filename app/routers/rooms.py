# Эндпоинты для работы с информацией о комнатах в отелях.

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import HotelDAO
from app.dependencies import get_db
from app.schemas import RoomResponse
from typing import List

router = APIRouter()

@router.get("/{hotel_id}/all")
async def list_rooms(hotel_id: int, db: AsyncSession = Depends(get_db)) -> List[RoomResponse]:
    hotel_dao = HotelDAO(db)
    rooms = await hotel_dao.get_rooms_by_hotel_id(hotel_id)
    return rooms

@router.get('/{hotel_id}')
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}'),
    db: AsyncSession = Depends(get_db)
) -> List[RoomResponse]:
    hotel_dao = HotelDAO(db)
    rooms = await hotel_dao.search_for_rooms(hotel_id, date_from, date_to)
    return rooms