#- **`dao.py` (Data Access Object)**: Эти классы и методы обеспечивают абстракцию для выполнения запросов к базе данных.
# Например, методы для получения пользователя по email, создания бронирования, проверки доступности номеров и т.д.

from typing import List, Optional
from sqlalchemy import exists, join, select, func, and_
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Users, Hotels, Rooms, Bookings
from datetime import date, datetime

class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Optional[Users]:
        query = select(Users).where(Users.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str) -> Users:
        user = Users(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

class HotelDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_hotels(self) -> List[Hotels]:
        query = select(Hotels)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_hotel_by_id(self, hotel_id: int) -> List[Hotels]:
        query = select(Hotels).where(Hotels.id == hotel_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_for_hotels(self, location: str, date_from: datetime.date, date_to: datetime.date) -> List[Hotels]: 
        """
        Асинхронно возвращает список отелей в указанном местоположении с доступными номерами на указанные даты.

        :param location: Местоположение отеля
        :param date_from: Дата начала периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :param date_to: Дата окончания периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :return: Список отелей, где есть доступные номера на указанные даты
        """
        
        async with self.session.begin():
            # Подготовим подзапрос для поиска свободных номеров
            free_rooms_subquery = (
                select(Rooms.hotel_id)
                .join(Bookings, Rooms.id == Bookings.room_id, isouter=True)
                .filter(
                    (Bookings.id == None) |
                    (Bookings.date_from >= date_to) |
                    (Bookings.date_to <= date_from)
                )
                .group_by(Rooms.hotel_id)
                .subquery()
            )

            # Основной запрос для получения отелей с доступными номерами и заданным местоположением
            query = (
                select(Hotels)
                .filter(Hotels.location.like(f'%{location}%'))
                .filter(Hotels.id.in_(select(free_rooms_subquery.c.hotel_id)))
            )

            result = await self.session.execute(query)
            hotels = result.scalars().all()

        return hotels

    async def get_rooms_by_hotel_id(self, hotel_id: int) -> List[Rooms]:
        query = select(Rooms).where(Rooms.hotel_id == hotel_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_for_rooms(self, hotel_id: int) -> List[Rooms]: #
        query = select(Rooms).where(Rooms.hotel_id == hotel_id)
        result = await self.session.execute(query)
        return result.scalars().all()

class BookingDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_bookings_by_user_id(self, user_id: int) -> List[Bookings]:
        query = select(Bookings).where(Bookings.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_booking(self, room_id: int, user_id: int, date_from: date, date_to: date, price: int) -> Bookings:
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
        # Get the total number of rooms of this type
        room_query = select(Rooms).where(Rooms.id == room_id)
        room_result = await self.session.execute(room_query)
        room = room_result.scalar_one_or_none()

        if room is None:
            return False

        total_rooms = room.quantity

        # Count the number of booked rooms for the given dates
        booking_query = select(Bookings).where(
            Bookings.room_id == room_id,
            Bookings.date_to > date_from,
            Bookings.date_from < date_to
        )
        booking_result = await self.session.execute(booking_query)
        overlapping_bookings = booking_result.scalars().all()
        booked_rooms = len(overlapping_bookings)

        # Check if there are any rooms available
        return booked_rooms < total_rooms

    async def get_price(self, room_id: int) -> bool:
        query = select(Rooms.price).filter_by(id=room_id)
        result = await self.session.execute(query)
        return result.scalar()