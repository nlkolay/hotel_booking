# Эндпоинты для работы с отелями, такие как получение списка отелей и комнат в отеле.

import asyncio
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import HotelDAO
from typing import List, Sequence
from fastapi_cache.decorator import cache

from app.database import get_db
from app.schemas import HotelResponse

router = APIRouter()

@router.get("/")
async def list_hotels(
    db: AsyncSession = Depends(get_db)
    ) -> Sequence[HotelResponse]:
    hotel_dao = HotelDAO(db)
    hotels = await hotel_dao.get_hotels()
    return hotels

@router.get("/{hotel_id}/")
async def get_hotel(
    hotel_id: int, 
    db: AsyncSession = Depends(get_db)
    ) -> Sequence[HotelResponse]:
    hotel_dao = HotelDAO(db)
    hotel = await hotel_dao.get_hotel_by_id(hotel_id)
    return hotel

@router.get('')
@cache(expire=20)
async def get_hotels_by_location_and_time(
    location: str = Query(..., description=f'Например, Алтай'),
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}'), 
    db: AsyncSession = Depends(get_db)
    ) -> Sequence[HotelResponse]:
    #await asyncio.sleep(3)
    hotel_dao = HotelDAO(db)
    hotels = await hotel_dao.search_for_hotels(location, date_from, date_to)
    if not hotels:
        raise HTTPException(status_code=404, detail="Нет доступных отелей на указанные даты.")
    return hotels