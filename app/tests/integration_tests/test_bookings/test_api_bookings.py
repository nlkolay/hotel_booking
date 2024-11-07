import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "room_id, date_from, date_to, booked_rooms, status_code",
    *[
        [(4, "2030-05-01", "2030-05-15", i, 201) for i in range(3, 11)]
        + [(4, "2030-05-01", "2030-05-15", 10, 400)] * 2
    ],
)
async def test_add_get_booking(
    room_id,
    date_from,
    date_to,
    booked_rooms,
    status_code,
    authenticated_ac: AsyncClient,
):
    # Add a new booking
    response = await authenticated_ac.post(
        "/bookings/create",
        json={"room_id": room_id, "date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "user",
    [
        {"email": "test@test.com", "password": "test"},
        {"email": "artem@example.com", "password": "artem"},
        # Добавьте других пользователей по мере необходимости
    ],
)
async def test_booking_crud(ac: AsyncClient, user):
    await ac.post("/auth/login", json=user)
    assert ac.cookies["session"]
    # Получаем все бронирования текущего пользователя
    response = await ac.get("/bookings/")
    assert response.status_code == 200
    bookings = response.json()

    # Удаляем все бронирования
    for booking in bookings:
        booking_id = booking["Bookings"]["id"]
        response = await ac.delete(f"/bookings/{booking_id}")
        assert response.status_code == 204

    # Проверяем, что бронирования были удалены
    response = await ac.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) == 0  # Убедитесь, что список пустой
