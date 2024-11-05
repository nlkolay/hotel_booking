# start: pytest -v [-s]
import json
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import pytest
from datetime import datetime
from sqlalchemy import insert
from httpx import AsyncClient
from app.main import app as fastapi_app
from app.database import Base, AsyncSessionLocal, engine
from app.config import settings
from app.models import Users, Bookings, Hotels, Rooms


@pytest.fixture(autouse=True, scope='module')
async def prepare_database():
    """
    Fixture to prepare the database for testing.

    This fixture is automatically used by pytest and sets up the database
    for testing by dropping and recreating the tables, and then populating
    them with mock data from JSON files.

    The mock data is loaded from the following files:
    - `app/tests/data/mock_hotels.json`
    - `app/tests/data/mock_rooms.json`
    - `app/tests/data/mock_users.json`
    - `app/tests/data/mock_bookings.json`

    The `date_from` and `date_to` fields in the `bookings` data are converted
    from ISO format strings to datetime objects.

    Example:
    To use this fixture in a test, simply define a test function without
    any arguments, like this:
    ```
    def test_my_test(prepare_database):
        # Your test code here
        pass
    ```
    The `prepare_database` fixture will be automatically run before the test
    function, setting up the database for testing.
    """
    assert settings.MODE == 'TEST'

    async with engine.begin() as conn:
        await  conn.run_sync(Base.metadata.drop_all)
        await  conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with  open(f'app/tests/data/mock_{model}.json', 'r') as file:
            return json.load(file)
        
    hotels = open_mock_json('hotels')
    rooms = open_mock_json('rooms')
    users = open_mock_json('users')
    bookings = open_mock_json('bookings')

    for booking in  bookings:
        booking["date_from"] = datetime.fromisoformat(booking.get("date_from"))
        booking["date_to"] = datetime.fromisoformat(booking.get("date_to"))

    async with  AsyncSessionLocal() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await  session.execute(add_hotels)
        await  session.execute(add_rooms)
        await  session.execute(add_users)
        await  session.execute(add_bookings)
        
        await  session.commit()


@pytest.fixture(scope='function')
async def ac():
    FastAPICache.init(InMemoryBackend())
    async with AsyncClient(app=fastapi_app, base_url='http://test') as ac:
        yield ac

@pytest.fixture(scope='session')
async def authenticated_ac():
    async with AsyncClient(app=fastapi_app, base_url='http://test') as ac:
        await  ac.post(
            "/auth/login", 
            json={
                "email": "test@test.com", 
                "password": "test"}
                )
        assert ac.cookies["session"]
        yield ac