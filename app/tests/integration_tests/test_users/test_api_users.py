from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("test@example.com", "password", 200),
        ("test@test.com", "password123", 400),
        ("kot@pes.com", "password", 200),
        ("kot", "password", 400),
    ],
)
async def test_register_user(
    email: str, password: str, expected_status: int, ac: AsyncClient
):
    """Test user registration with various email and password combinations."""

    # Prepare the registration payload
    registration_payload = {
        "email": email,
        "password": password,
    }

    # Send a POST request to the registration endpoint
    response = await ac.post("/auth/register", json=registration_payload)

    # Assert that the response status code matches the expected status code
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("test@test.com", "test", 200),
        ("test@test.com", "test1", 401),
        ("artem@example.com", "artem", 200),
        ("kot", "password", 401),
    ],
)
async def test_login_user(
    email: str, password: str, expected_status: int, ac: AsyncClient
):
    """Test user login with various email and password combinations."""

    # Prepare the login payload
    login_payload = {
        "email": email,
        "password": password,
    }

    # Send a POST request to the login endpoint
    response = await ac.post("/auth/login", json=login_payload)

    # Assert that the response status code matches the expected status code
    assert response.status_code == expected_status
