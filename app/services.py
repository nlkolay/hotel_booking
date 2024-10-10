# Сервисы - слой логики для эндпоинтов, не привязанный к конкретному API. Вызывается роутером, обращается к 
# DAO/Repo, внешнему API, другим сервисам и т.д.
# Здесь для примера (логика перенесена частично).

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BookingDAO
from app.models import Users
from app.schemas import BookingCreate

class BookingService:
    @classmethod
    async def create_booking(
        cls,
        booking: BookingCreate,
        background_tasks: BackgroundTasks,
        current_user: Users,
        db: AsyncSession
    ):
        booking_dao = BookingDAO(db)

        # Проверка доступности комнаты
        is_available = await booking_dao.is_room_available(booking.room_id, booking.date_from, booking.date_to)
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Комната недоступна на выбранные даты"
            )

        price = await booking_dao.get_price(booking.room_id)

        new_booking = await booking_dao.create_booking(
            room_id=booking.room_id,
            user_id=current_user.id,
            date_from=booking.date_from,
            date_to=booking.date_to,
            price=price
        )


        return new_booking