# Эндпоинты для управления бронированиями, включая создание, получение списка и удаление бронирований.

from typing import Dict, List, Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, status

# from fastapi_versioning import version
from pydantic import TypeAdapter, ValidationError

from app.dao import BookingDAO
from app.dependencies import get_current_user
from app.exceptions import BookingNotFound
from app.models import Bookings, Rooms, Users
from app.schemas import BookingBase, BookingCreate, BookingResponseExtended
from app.services import BookingService

router = APIRouter()

@router.post("/create", status_code=status.HTTP_201_CREATED)
# @version(1)
async def new_booking(
    booking: BookingCreate,
    background_tasks: BackgroundTasks,
    current_user: Users = Depends(get_current_user),
) -> BookingBase:
    new_booking = await BookingService.create_booking(
        booking, background_tasks, current_user
    )
    # deprecated (validation workaround):
    # booking_dict = obj_to_dict(new_booking)

    # вариант с celery:
    # send_booking_confirmation_email.delay(booking_dict, current_user.email)

    # вариант встроенный в fastapi с BackgroundTasks:
    # background_tasks.add_task(send_booking_confirmation_email, booking_dict, current_user.email)
    # OSError: [Errno 101] Network is unreachable -
    # probably, port is blocked

    return new_booking


@router.get("/")
# @version(1)
async def list_bookings(
    current_user: Users = Depends(get_current_user),
) -> Sequence[BookingResponseExtended]:
    bookings = await BookingDAO.get_bookings_by_user_id(current_user.id)
    # Выше пример с использованием relationship алхимии
    #
    # try:
    #     validated_data = BookingResponseExtended(bookings=bookings)
    #     return validated_data
    # except ValueError as e:
    #     raise HTTPException(status_code=400, detail=str(e))
    return bookings


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
# @version(1)
async def delete_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user)
    ) -> None:
    booking = await BookingDAO.get_booking_by_id(booking_id)
    if booking is None or booking.user_id != current_user.id:
        raise BookingNotFound
    await BookingDAO.delete_booking(booking)
    return
