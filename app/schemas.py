# Здесь определены схемы Pydantic, которые используются для валидации данных, получаемых и отправляемых через API. Эти схемы описывают структуру данных, которая будет передаваться между клиентом и сервером.

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

class HotelResponse(BaseModel):
    id: int
    name: str
    location: str
    services: List[str]
    rooms_quantity: int
    image_id: int

class RoomResponse(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: List[str]
    quantity: int
    image_id: int

class BookingCreate(BaseModel):
    room_id: int
    date_from: date
    date_to: date

class BookingResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
