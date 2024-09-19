from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BookingDAO
from app.dependencies import get_db, get_current_active_user, get_current_user
from app.models import Bookings, Rooms
from app.schemas import BookingCreate, BookingResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    booking_dao = BookingDAO(db)

    # Check room availability
    is_available = await booking_dao.is_room_available(booking.room_id, booking.date_from, booking.date_to)
    if not is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is not available for the selected dates")


    price = await booking_dao.get_price(booking.room_id)

    new_booking = await booking_dao.create_booking(
        room_id=booking.room_id,
        user_id=current_user.id,
        date_from=booking.date_from,
        date_to=booking.date_to,
        price=price
    )

    await db.commit()
    await db.refresh(new_booking)

    return new_booking

@router.get("/", response_model=List[BookingResponse])
async def list_bookings(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_active_user)):
    booking_dao = BookingDAO(db)
    bookings = await booking_dao.get_bookings_by_user_id(current_user.id)
    return bookings

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    booking_dao = BookingDAO(db)
    booking = await booking_dao.get_booking_by_id(booking_id)
    if booking is None or booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    await booking_dao.delete_booking(booking)
    return