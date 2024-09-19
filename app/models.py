from sqlalchemy import Column, Integer, String, ForeignKey, Date, Computed, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from typing import Optional
from datetime import date

class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

class Hotels(Base):
    __tablename__ = "hotels"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str] = mapped_column(String)
    services: Mapped[list[str]] = mapped_column(JSON)
    rooms_quantity: Mapped[int] = mapped_column(Integer)
    image_id: Mapped[int] = mapped_column(Integer)

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

class Bookings(Base):
    __tablename__ = 'bookings'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)
    price: Mapped[int] = mapped_column(Integer)
    total_cost: Mapped[int] = mapped_column(Computed("(date_to - date_from) * price"))
    total_days: Mapped[int] = mapped_column(Computed("date_to - date_from"))
