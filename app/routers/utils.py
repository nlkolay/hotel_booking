import csv
import io
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.database import AsyncSessionLocal  # Импортируем асинхронную сессию
from app.models import Bookings, Hotels, Rooms
from app.schemas import BookingBase, HotelBase, RoomBase

router = APIRouter(prefix="/upload", tags=["CSV Upload"])

def parse_csv_file(file: UploadFile, model_type: str):
    """
    Универсальный парсер CSV файлов
    """
    try:
        content = file.file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content), delimiter=';')
        next(reader, None)  # Пропускаем заголовок

        parsed_data = []

        if model_type == 'hotel':
            for row in reader:
                hotel = HotelBase(
                    name=row[0],
                    location=row[1],
                    services=eval(row[2]),  # Преобразуем строку списка в список
                    rooms_quantity=int(row[3]),
                    image_id=int(row[4])
                )
                parsed_data.append(hotel)

        elif model_type == 'room':
            for row in reader:
                room = RoomBase(
                    hotel_id=int(row[0]),
                    name=row[1],
                    description=row[2] or None,
                    price=int(row[3]),
                    services=eval(row[4]),
                    quantity=int(row[5]),
                    image_id=int(row[6])
                )
                parsed_data.append(room)

        elif model_type == 'booking':
            for row in reader:
                booking = BookingBase(
                    room_id=int(row[0]),
                    user_id=int(row[1]),
                    date_from=row[2],
                    date_to=row[3],
                    price=int(row[4])
                )
                parsed_data.append(booking)

        return parsed_data

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка парсинга файла: {str(e)}")

@router.post("/hotels")
async def upload_hotels(
    file: UploadFile = File(...)
):
    """
    Загрузка отелей из CSV
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть CSV")

    try:
        # Используем асинхронную сессию
        async with AsyncSessionLocal() as session:
            hotels_data = parse_csv_file(file, 'hotel')

            db_hotels = [
                Hotels(
                    name=hotel.name,
                    location=hotel.location,
                    services=hotel.services,
                    rooms_quantity=hotel.rooms_quantity,
                    image_id=hotel.image_id
                ) for hotel in hotels_data
            ]

            session.add_all(db_hotels)
            await session.commit()

            return {
                "status": "success",
                "uploaded_count": len(db_hotels)
            }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")

@router.post("/rooms")
async def upload_rooms(
    file: UploadFile = File(...)
):
    """
    Загрузка номеров из CSV
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть CSV")

    try:
        async with AsyncSessionLocal() as session:
            rooms_data = parse_csv_file(file, 'room')

            db_rooms = [
                Rooms(
                    hotel_id=room.hotel_id,
                    name=room.name,
                    description=room.description,
                    price=room.price,
                    services=room.services,
                    quantity=room.quantity,
                    image_id=room.image_id
                ) for room in rooms_data
            ]

            session.add_all(db_rooms)
            await session.commit()

            return {
                "status": "success",
                "uploaded_count": len(db_rooms)
            }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")

@router.post("/bookings")
async def upload_bookings(
    file: UploadFile = File(...)
):
    """
    Загрузка бронирований из CSV
    ВНИМАНИЕ!
    Сначала:
     1. Должны зарегистрироваться первые ДВА пользователя.
     2. Должны быть созданы отели и комнаты.
     Затем можно загружать бронирования.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть CSV")

    try:
        async with AsyncSessionLocal() as session:
            bookings_data = parse_csv_file(file, 'booking')

            db_bookings = [
                Bookings(
                    room_id=booking.room_id,
                    user_id=booking.user_id,
                    date_from=booking.date_from,
                    date_to=booking.date_to,
                    price=booking.price
                ) for booking in bookings_data
            ]

            session.add_all(db_bookings)
            await session.commit()

            return {
                "status": "success",
                "uploaded_count": len(db_bookings)
            }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
