# В этом файле определяются модели базы данных с использованием SQLAlchemy.
# Эти модели соответствуют таблицам в базе данных и используются для CRUD операций.

from sqlalchemy import Integer, String, ForeignKey, Date, Computed, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from typing import Optional
from datetime import date


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    bookings: Mapped[list["Bookings"]] = relationship(back_populates="user")

    def __str__(self):
        return f"Пользователь {self.email}"


class Hotels(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str] = mapped_column(String)
    services: Mapped[list[str]] = mapped_column(JSON)
    rooms_quantity: Mapped[int] = mapped_column(Integer)
    image_id: Mapped[int] = mapped_column(Integer)

    rooms: Mapped[list["Rooms"]] = relationship(back_populates="hotel")

    def __str__(self):
        return f'Отель "{self.name}"; {self.location[:30]}'


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    services: Mapped[list[str]] = mapped_column(JSON)
    quantity: Mapped[int] = mapped_column(Integer)
    image_id: Mapped[int] = mapped_column(Integer)

    hotel: Mapped["Hotels"] = relationship(back_populates="rooms")
    bookings: Mapped[list["Bookings"]] = relationship(back_populates="room")

    def __str__(self):
        return f'Номер "{self.name}"'


class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int] = mapped_column(Integer)
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))

    user: Mapped["Users"] = relationship(back_populates="bookings")
    room: Mapped["Rooms"] = relationship(back_populates="bookings")

    def __str__(self):
        return f"Бронирование №{self.id}"


# class Bookings_extended(Bookings):
#     #extend_existing=True
#     hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
#     hotel_name: Mapped[str] = mapped_column(ForeignKey("hotels.name"))
#     location: Mapped[str] = mapped_column(ForeignKey("hotels.location"))
#     room_name: Mapped[str] = mapped_column(ForeignKey("rooms.name"))
