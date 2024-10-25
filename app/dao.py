#- **`dao.py` (Data Access Object)**: Эти классы и методы обеспечивают абстракцию для выполнения запросов к базе данных.
# Например, методы для получения пользователя по email, создания бронирования, проверки доступности номеров и т.д.

from typing import List, Optional, Sequence
from pydantic import EmailStr
from sqlalchemy import RowMapping, exists, join, label, null, select, func, and_
from sqlalchemy.orm import Query, selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import  Users, Hotels, Rooms, Bookings
from datetime import date, datetime

class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: EmailStr) -> Optional[Users]:
        query = select(Users).where(Users.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, email: EmailStr, hashed_password: str) -> Users:
        user = Users(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
class HotelDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_hotels(self) -> Sequence[Hotels]:
        query = select(Hotels)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_hotel_by_id(self, hotel_id: int) -> Sequence[Hotels]:
        query = select(Hotels).where(Hotels.id == hotel_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_for_hotels(self, location: str, date_from: date, date_to: date) -> Sequence[Hotels]: 
        """
        Возвращает список отелей в указанном местоположении с доступными номерами на указанные даты.

        :param location: Местоположение отеля
        :param date_from: Дата начала периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :param date_to: Дата окончания периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :return: Список отелей, где есть доступные номера на указанные даты
        """
        #async with self.session.begin():
        # Подготовим подзапрос для поиска свободных номеров
        booked_rooms_cte = (
            select(
                Bookings.room_id, 
                func.count().label('booked_count')
                )
            .where(
                (
                (Bookings.date_from >= date_from) &
                (Bookings.date_from <= date_to)
                ) |
                (
                (Bookings.date_from <= date_from) &
                (Bookings.date_to > date_from)
                )
                )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )
        free_rooms_subquery = (
            select(Rooms.hotel_id)
            .join(booked_rooms_cte, Rooms.id == booked_rooms_cte.c.room_id, isouter=True)
            .where(
                    (booked_rooms_cte.c.booked_count.is_(None)) |
                    (Rooms.quantity > booked_rooms_cte.c.booked_count)
            )
            .cte('free_rooms')
        )

        # Основной запрос для получения отелей с доступными номерами и заданным местоположением
        # TODO 
        # 1. Использование полнотекстового поиска: Для более сложных запросов можно использовать функциональность полнотекстового 
        # поиска, если это поддерживает используемая СУБД.
        # 2. Преобразование в нормализованную форму: Чтобы искать вне зависимости от чисел, 
        # диакритических знаков и других вариантов написания.
        query = (
            select(Hotels)
            .where(Hotels.location.ilike(f'%{location.lower()}%'))
            .where(Hotels.id.in_(select(free_rooms_subquery.c.hotel_id)))
        )

        result = await self.session.execute(query)
        hotels = result.scalars().all()

        return hotels

    async def get_rooms_by_hotel_id(self, hotel_id: int) -> Sequence[Rooms]:
        query = select(Rooms).where(Rooms.hotel_id == hotel_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_for_rooms(self, hotel_id: int, date_from: date, date_to: date) -> Sequence[Rooms]:
        booked_rooms_cte = (
            select(
                Bookings.room_id, 
                func.count().label('booked_count')
                )
            .where(
                (
                (Bookings.date_from >= date_from) &
                (Bookings.date_from <= date_to)
                ) |
                (
                (Bookings.date_from <= date_from) &
                (Bookings.date_to > date_from)
                )
                )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )
        query = (
            select(Rooms)
            .join(booked_rooms_cte, Rooms.id == booked_rooms_cte.c.room_id, isouter=True)
            .where(
                (Rooms.hotel_id == hotel_id) &
                (
                    (booked_rooms_cte.c.booked_count.is_(None)) |
                    (Rooms.quantity > booked_rooms_cte.c.booked_count)
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

class BookingDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_bookings_by_user_id(self, user_id: int) -> Sequence[RowMapping]:
        query = (
            select(Bookings)
            .options(joinedload(Bookings.room))
            .options(joinedload(Bookings.room).subqueryload(Rooms.hotel))
            .where(Bookings.user_id == user_id)
        )   
        # query = (
        #     select(
        #         Bookings, Hotels, Rooms
        #         )
        #     .outerjoin(Rooms, Bookings.room_id == Rooms.id)
        #     .outerjoin(Hotels, Rooms.hotel_id == Hotels.id)
        #     .where(Bookings.user_id == user_id)
        # )
        result = await self.session.execute(query)
        return result.mappings().all()
         
    async def create_booking(self, room_id: int, user_id: int, date_from: date, date_to: date, price: int) -> Optional[Bookings]:
        booking = Bookings(room_id=room_id, user_id=user_id, date_from=date_from, date_to=date_to, price=price)
        self.session.add(booking)
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def get_booking_by_id(self, booking_id: int) -> Optional[Bookings]:
        query = select(Bookings).where(Bookings.id == booking_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_booking(self, booking: Bookings):
        await self.session.delete(booking)
        await self.session.commit()

    async def is_room_available(self, room_id: int, date_from: date, date_to: date) -> bool:
        subq = (
            select(
                func.count().label('booked_count')
                )
            .select_from(Rooms)
            .outerjoin(Bookings, Bookings.room_id == Rooms.id)
            .where(
                (Bookings.room_id == room_id) &
                (
                (
                (Bookings.date_from >= date_from) &
                (Bookings.date_from <= date_to)
                ) |
                (
                (Bookings.date_from <= date_from) &
                (Bookings.date_to > date_from)
                )
                )
                )
        )

        query = select(Rooms.quantity > subq.c.booked_count).where(Rooms.id == room_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_price(self, room_id: int) -> int:
        query = select(Rooms.price).where(Rooms.id == room_id)
        result = await self.session.execute(query)
        return result.scalar_one()