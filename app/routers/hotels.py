# Эндпоинты для работы с отелями, такие как получение списка отелей и комнат в отеле.

from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import HotelDAO
from app.dependencies import get_db
from app.schemas import HotelResponse, RoomResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[HotelResponse])
async def list_hotels(db: AsyncSession = Depends(get_db)):
    hotel_dao = HotelDAO(db)
    hotels = await hotel_dao.get_hotels()
    return hotels

@router.get("/{hotel_id}/", response_model=List[HotelResponse])
async def get_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    hotel_dao = HotelDAO(db)
    hotel = await hotel_dao.get_hotel_by_id(hotel_id)
    return hotel

@router.get('')
async def get_hotels_by_location_and_time(
    location: str = Query(..., description=f'Например, Алтай'),
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}'), 
    db: AsyncSession = Depends(get_db)
) -> List[HotelResponse]:
    hotel_dao = HotelDAO(db)
    hotels = await hotel_dao.search_for_hotels(location, date_from, date_to)
    if not hotels:
        raise HTTPException(status_code=404, detail="Нет доступных отелей на указанные даты.")
    return hotels