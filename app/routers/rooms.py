# Эндпоинты для работы с информацией о комнатах в отелях.

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from app.dao import HotelDAO
from typing import List, Sequence

from app.schemas import RoomBase, RoomResponse  

router = APIRouter()

@router.get("/{hotel_id}/all")
async def list_rooms(
    hotel_id: int
    ) -> Sequence[RoomBase]:
    rooms = await HotelDAO.get_rooms_by_hotel_id(hotel_id)
    return rooms

@router.get('/{hotel_id}')
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}'),
    ) -> Sequence[RoomBase]:
    rooms = await HotelDAO.search_for_rooms(hotel_id, date_from, date_to)
    return rooms