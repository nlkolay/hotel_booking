# - **`dao.py` (Data Access Object)**: Эти классы и методы обеспечивают абстракцию для выполнения запросов к базе данных.
# Например, методы для получения пользователя по email, создания бронирования, проверки доступности номеров и т.д.

from typing import Optional, Sequence
from pydantic import EmailStr
from sqlalchemy import and_, or_, select, func
from sqlalchemy.orm import selectinload, joinedload
from datetime import date
from app.models import Users, Hotels, Rooms, Bookings
from app.schemas import (
    BookingBase,
    BookingResponseExtended,
    HotelResponse,
    RoomResponse,
    UserResponse,
)
from app.database import AsyncSessionLocal


class UserDAO:
    @classmethod
    async def get_user_by_email(cls, email: EmailStr) -> Optional[UserResponse]:
        query = select(Users).where(Users.email == email)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, email: EmailStr, hashed_password: str) -> UserResponse:
        user = Users(email=email, hashed_password=hashed_password)
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


class HotelDAO:
    @classmethod
    async def get_hotels(cls) -> Sequence[HotelResponse]:
        query = select(Hotels)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_hotel_by_id(cls, hotel_id: int) -> Sequence[HotelResponse]:
        query = select(Hotels).where(Hotels.id == hotel_id)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def search_for_hotels(
        cls, location: str, date_from: date, date_to: date
    ) -> Sequence[HotelResponse]:
        """
        Возвращает список отелей в указанном местоположении с доступными номерами на указанные даты.

        :param location: Местоположение отеля
        :param date_from: Дата начала периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :param date_to: Дата окончания периода поиска свободных номеров (в формате 'YYYY-MM-DD')
        :return: Список отелей, где есть доступные номера на указанные даты
        """
        # async with session.begin():
        # Подготовим подзапрос для поиска свободных номеров
        booked_rooms_cte = (
            select(Bookings.room_id, func.count().label("booked_count"))
            .where(
                ((Bookings.date_from >= date_from) & (Bookings.date_from <= date_to))
                | ((Bookings.date_from <= date_from) & (Bookings.date_to > date_from))
            )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )
        free_rooms_subquery = (
            select(Rooms.hotel_id)
            .join(
                booked_rooms_cte, Rooms.id == booked_rooms_cte.c.room_id, isouter=True
            )
            .where(
                (booked_rooms_cte.c.booked_count.is_(None))
                | (Rooms.quantity > booked_rooms_cte.c.booked_count)
            )
            .cte("free_rooms")
        )

        # Основной запрос для получения отелей с доступными номерами и заданным местоположением
        # TODO
        # 1. Использование полнотекстового поиска: Для более сложных запросов можно использовать функциональность полнотекстового
        # поиска, если это поддерживает используемая СУБД.
        # 2. Преобразование в нормализованную форму: Чтобы искать вне зависимости от чисел,
        # диакритических знаков и других вариантов написания.
        query = (
            select(Hotels)
            .where(Hotels.location.ilike(f"%{location.lower()}%"))
            .where(Hotels.id.in_(select(free_rooms_subquery.c.hotel_id)))
        )

        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        hotels = result.scalars().all()

        return hotels

    @classmethod
    async def get_rooms_by_hotel_id(cls, hotel_id: int) -> Sequence[RoomResponse]:
        query = select(Rooms).where(Rooms.hotel_id == hotel_id)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def search_for_rooms(
        cls, hotel_id: int, date_from: date, date_to: date
    ) -> Sequence[RoomResponse]:
        booked_rooms_cte = (
            select(Bookings.room_id, func.count().label("booked_count"))
            .where(
                ((Bookings.date_from >= date_from) & (Bookings.date_from <= date_to))
                | ((Bookings.date_from <= date_from) & (Bookings.date_to > date_from))
            )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )
        query = (
            select(Rooms)
            .join(
                booked_rooms_cte, Rooms.id == booked_rooms_cte.c.room_id, isouter=True
            )
            .where(
                (Rooms.hotel_id == hotel_id)
                & (
                    (booked_rooms_cte.c.booked_count.is_(None))
                    | (Rooms.quantity > booked_rooms_cte.c.booked_count)
                )
            )
        )
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalars().all()


class BookingDAO:
    # Пример с использованием relationship алхимии:
    @classmethod
    async def get_bookings_by_user_id(
        cls, user_id: int
    ) -> Sequence[BookingResponseExtended]:
        query = (
            select(Bookings)
            .options(joinedload(Bookings.room))
            .options(joinedload(Bookings.room).subqueryload(Rooms.hotel))
            .where(Bookings.user_id == user_id)
        )
        # Который заменил:
        # query = (
        #     select(
        #         Bookings, Hotels, Rooms
        #         )
        #     .outerjoin(Rooms, Bookings.room_id == Rooms.id)
        #     .outerjoin(Hotels, Rooms.hotel_id == Hotels.id)
        #     .where(Bookings.user_id == user_id)
        # )
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.mappings().all()

    @classmethod
    async def add_booking(
        cls, room_id: int, user_id: int, date_from: date, date_to: date, price: int
    ) -> BookingBase:
        booking = Bookings(
            room_id=room_id,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            price=price,
        )
        async with AsyncSessionLocal() as session:
            session.add(booking)
            await session.commit()
            await session.refresh(booking)
        return booking

    @classmethod
    async def get_booking_by_id(
        cls, booking_id: int
    ) -> Optional[BookingResponseExtended]:
        query = select(Bookings).where(Bookings.id == booking_id)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def delete_booking(cls, booking: Bookings) -> None:
        async with AsyncSessionLocal() as session:
            await session.delete(booking)
            await session.commit()

    @classmethod
    async def is_room_available(
        cls, room_id: int, date_from: date, date_to: date
    ) -> bool:
        subq = (
            select(func.count().label("booked_count"))
            .select_from(Bookings)
            .where(
                and_(
                    Bookings.room_id == room_id,
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                    ),
                )
            )
            .correlate(Rooms)
            .scalar_subquery()
        )

        query = select(Rooms.quantity > subq).where(Rooms.id == room_id)

        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
            return result.scalar_one()

    @classmethod
    async def get_price(cls, room_id: int) -> int:
        query = select(Rooms.price).where(Rooms.id == room_id)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalar_one()

    # TODO:
    # непонятно как это сделать:
    # AttributeError: 'classmethod' object has no attribute 'execute'
    # переделать обращения к БД по образцу db from database.py
    # async def session():
    #     async with AsyncSessionLocal() as session:
    #         yield session
