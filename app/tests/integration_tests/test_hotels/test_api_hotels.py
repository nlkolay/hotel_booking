from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.fixture
def base_url():
    return "/hotels"


@pytest.mark.parametrize(
    "date_from,date_to,expected_status,expected_response",
    [
        # Тест 1: Дата заезда равна дате выезда (неверные параметры)
        (
            datetime.now().date(),
            datetime.now().date(),
            400,
            {
                "detail": "Дата начала бронирования должна быть меньше или равна дате окончания."
            },
        ),
        # Тест 2: Разница между датами > 30 дней (неверные параметры)
        (
            datetime.now().date(),
            datetime.now().date() + timedelta(days=31),
            400,
            {"detail": "Длительность бронирования не может превышать 30 дней."},
        ),
        # Тест 3: Корректные даты (верные параметры)
        (datetime.now().date(), datetime.now().date() + timedelta(days=10), 200, None),
    ],
)
async def test_get_hotels_by_location_and_time(
    ac: AsyncClient, base_url, date_from, date_to, expected_status, expected_response
):
    response = await ac.get(
        base_url,
        params={"location": "Алтай", "date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == expected_status

    if expected_response:
        assert response.json() == expected_response
    else:
        # Для успешного ответа проверяем, что возвращается список
        assert isinstance(response.json(), list)


@pytest.mark.parametrize(
    "location,expected_status",
    [
        ("", 422),  # Пустая локация должна вызывать ошибку валидации
        ("Алтай", 200),  # Корректная локация
    ],
)
async def test_location_validation(
    ac: AsyncClient, base_url, location, expected_status
):
    date_from = datetime.now().date()
    date_to = date_from + timedelta(days=5)

    response = await ac.get(
        base_url,
        params={"location": location, "date_from": date_from, "date_to": date_to},
    )

    assert response.status_code == expected_status


async def test_no_vacation(ac: AsyncClient, base_url):
    # Предполагаем, что для этой локации и дат нет доступных отелей
    response = await ac.get(
        base_url,
        params={
            "location": "НесуществующееМесто",
            "date_from": datetime.now().date(),
            "date_to": datetime.now().date() + timedelta(days=5),
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Нет доступных номеров на указанные даты."}
