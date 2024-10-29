# Эндпоинты для управления бронированиями, включая создание, получение списка и удаление бронирований.

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BookingDAO
from app.database import get_db
from app.dependencies import get_current_active_user, get_current_user
from app.models import Bookings, Rooms, Users
from app.schemas import BookingBase, BookingCreate, BookingResponseExtended
from typing import List, Dict, Sequence

from pydantic import TypeAdapter, ValidationError

from app.services import BookingService
from app.log import logger, handler
from app.utils import obj_to_dict


router = APIRouter()


@router.post("/create", status_code=201)
async def create_booking(
    booking: BookingCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user)
    ) -> BookingBase:    
    new_booking = await BookingService.create_booking(
        booking,
        background_tasks,
        current_user,
        db
    )
    # booking_dict = obj_to_dict(new_booking)
    # вариант с celery
    # send_booking_confirmation_email.delay(booking_dict, current_user.email) 

    # вариант встроенный в fastapi с BackgroundTasks
    #background_tasks.add_task(send_booking_confirmation_email, booking_dict, current_user.email)
    # OSError: [Errno 101] Network is unreachable - 
    # probably, port is blocked

    return new_booking


@router.get("/")
async def list_bookings(
    db: AsyncSession = Depends(get_db), 
    current_user=Depends(get_current_active_user)
    ) -> Sequence[BookingResponseExtended]:
    booking_dao = BookingDAO(db)
    bookings = await booking_dao.get_bookings_by_user_id(current_user.id)
    # Выше пример с использованием relationship алхимии
    # 
    # try:
    #     validated_data = BookingResponseExtended(bookings=bookings)
    #     return validated_data
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    return bookings


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user=Depends(get_current_user)
    ):
    booking_dao = BookingDAO(db)
    booking = await booking_dao.get_booking_by_id(booking_id)
    if booking is None or booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    await booking_dao.delete_booking(booking)
    return
