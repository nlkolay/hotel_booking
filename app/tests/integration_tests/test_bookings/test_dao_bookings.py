from datetime import date
from app.dao import BookingDAO
import pytest


@pytest.mark.parametrize(
    'room_id, user_id, date_from, date_to, price', [
    (2, 2, '2024-10-10', '2024-10-12', 1000),
    (2, 2, '2024-10-10', '2023-10-12', 1000),
    # (2, 3, '2024-10-10', '2024-10-12', 1000),
    # asyncpg.exceptions.ForeignKeyViolationError
    (2, 2, '2024-10-10', '2024-10-12', -1000),
]
)
async def test_add_get_booking(
    room_id: int,
    user_id: int,
    date_from: str,
    date_to: str,
    price: int):
    # Create a new booking
    new_booking = await BookingDAO.add_booking(
        room_id=room_id,
        user_id=user_id,
        date_from=date.fromisoformat(date_from),
        date_to=date.fromisoformat(date_to),
        price=price
        )

    # Validate the booking creation
    # assert new_booking.id == 4, "Booking ID does not match expected value."
    assert new_booking.room_id == room_id, "Room ID does not match expected value."
    assert new_booking.user_id == user_id, "User  ID does not match expected value."

    # Check the price of the booking
    real_price = await BookingDAO.get_price(new_booking.room_id)
    assert isinstance(real_price, int), "Real price should be of type int."

    # Retrieve the booking by ID and validate it exists
    retrieved_booking = await BookingDAO.get_booking_by_id(new_booking.id)
    assert retrieved_booking is not None, "Booking should exist after creation."

    # Delete the booking and confirm deletion
    await BookingDAO.delete_booking(retrieved_booking)
    deleted_booking = await BookingDAO.get_booking_by_id(new_booking.id)
    assert deleted_booking is None, "Booking should be deleted and not found."
