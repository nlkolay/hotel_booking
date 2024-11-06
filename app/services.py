# Сервисы - слой логики для эндпоинтов, не привязанный к конкретному API.
# Вызывается роутером, обращается к
# DAO/Repo, внешнему API, другим сервисам и т.д.
# Здесь для примера.

from fastapi import BackgroundTasks
from app.exceptions import RoomIsNotAvailable
from app.models import Users
from app.schemas import BookingCreate
from app.dao import BookingDAO


class BookingService:
    @classmethod
    async def create_booking(
        cls,
        booking: BookingCreate,
        background_tasks: BackgroundTasks,
        current_user: Users,
    ):
        # Проверка доступности комнаты
        is_available = await BookingDAO.is_room_available(
            booking.room_id, booking.date_from, booking.date_to
        )
        if not is_available:
            raise RoomIsNotAvailable

        price = await BookingDAO.get_price(booking.room_id)

        new_booking = await BookingDAO.add_booking(
            room_id=booking.room_id,
            user_id=current_user.id,
            date_from=booking.date_from,
            date_to=booking.date_to,
            price=price,
        )

        return new_booking
