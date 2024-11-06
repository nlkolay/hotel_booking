# Эндпоинты для работы с отелями, такие как получение списка отелей и комнат в отеле.

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from app.dao import HotelDAO
from typing import List, Sequence
from fastapi_cache.decorator import cache

from app.exceptions import DatesInvalid, NoVacation, TooLong
from app.schemas import HotelResponse

router = APIRouter()

@router.get("/")
async def list_hotels() -> Sequence[HotelResponse]:
    hotels = await HotelDAO.get_hotels()
    return hotels

@router.get("/{hotel_id}/")
async def get_hotel(
    hotel_id: int
    ) -> Sequence[HotelResponse]:
    hotel = await HotelDAO.get_hotel_by_id(hotel_id)
    return hotel

@router.get('')
@cache(expire=20)
async def get_hotels_by_location_and_time(
    location: str = Query(..., min_length=1, description=f'Например, Алтай'),
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}')
    ) -> Sequence[HotelResponse]:
    #await asyncio.sleep(3)
    if date_from >= date_to:
        raise DatesInvalid
    if (date_to - date_from).days > 30:
        raise TooLong
    hotels = await HotelDAO.search_for_hotels(location, date_from, date_to)
    if not hotels:
        raise NoVacation
    return hotels
