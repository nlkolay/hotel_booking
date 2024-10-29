# Эндпоинты для работы с информацией о комнатах в отелях.

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import HotelDAO
from app.dependencies import get_db
from typing import List, Sequence

from sqlalchemy.orm import selectinload, joinedload

from app.models import Bookings, Hotels, Rooms
from app.schemas import RoomBase, RoomResponse  

router = APIRouter()

@router.get("/{hotel_id}/all")
async def list_rooms(
    hotel_id: int, 
    db: AsyncSession = Depends(get_db)
    ) -> Sequence[RoomBase]:
    hotel_dao = HotelDAO(db)
    rooms = await hotel_dao.get_rooms_by_hotel_id(hotel_id)
    return rooms

@router.get('/{hotel_id}')
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(..., description=f'Например, {datetime.now().date()}'),
    date_to: date = Query(..., description=f'Например, {datetime.now().date()}'),
    db: AsyncSession = Depends(get_db)
    ) -> Sequence[RoomBase]:
    hotel_dao = HotelDAO(db)
    rooms = await hotel_dao.search_for_rooms(hotel_id, date_from, date_to)
    return rooms


@router.get("/example/no_orm")
async def get_noorm(session: AsyncSession = Depends(get_db)):
    query = (
        select(
            Rooms, 
            Hotels, 
            Bookings
        )
        .join(Hotels, Rooms.hotel_id==Hotels.id)
        .join(Bookings, Bookings.room_id==Rooms.id)
    )
    res = await session.execute(query)
    res = res.mappings().all()
    return res


@router.get("/example/orm")
async def get_noorm(session: AsyncSession = Depends(get_db)):
    query = (
        select(Rooms)
        .options(joinedload(Rooms.hotel))
        .options(selectinload(Rooms.bookings))
    )
    res = await session.execute(query)
    res = res.scalars().all()
    #res = jsonable_encoder(res)
    return res
