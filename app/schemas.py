# Здесь определены схемы Pydantic, которые используются для валидации данных, получаемых и отправляемых через API. 
# Эти схемы описывают структуру данных, которая будет передаваться между клиентом и сервером.

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str

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

class RoomBase(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: Optional[str]
    price: int
    services: List[str]
    quantity: int
    image_id: int

class RoomResponse(RoomBase):
    hotel: HotelResponse

class BookingCreate(BaseModel):
    room_id: int
    date_from: date
    date_to: date

class BookingBase(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

class BookingResponse(BookingBase):
    room: RoomResponse

class BookingResponseExtended(BaseModel):
    Bookings: BookingResponse

    # id: int
    # room_id: int
    # user_id: int
    # date_from: date
    # date_to: date
    # price: int
    # total_cost: int
    # total_days: int
    # room: RoomResponseExtended    
    
    # bookings: List[BookingResponse]

    # @field_validator("bookings")
    # def validate_bookings(cls, value):
    #     if not isinstance(value, list):
    #         raise ValueError("Bookings must be a list")
    #     for booking_data in value:
    #         if not isinstance(booking_data, dict):
    #             raise ValueError("Each booking must be a dictionary")
    #         if "hotel" not in booking_data or not isinstance(booking_data["hotel"], dict):
    #             raise ValueError("Each booking must have a valid 'hotel' dictionary")
    #         if "room" not in booking_data or not isinstance(booking_data["room"], dict):
    #             raise ValueError("Each booking must have a valid 'room' dictionary")
    #     return value