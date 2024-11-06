from datetime import date, timedelta
from typing import Optional, Sequence
from pydantic import EmailStr
from sqlalchemy import select

from app.models import Bookings, Users
from app.database import AsyncSessionLocal


class TaskDAO:
    @classmethod
    async def get_email_by_booking(cls, booking: Bookings) -> EmailStr:
        query = select(Users.email).where(Users.id == booking.user_id)
        async with AsyncSessionLocal() as session:
            email = await session.execute(query)
        return email.scalar_one_or_none()

    @classmethod
    async def get_booking_by_days_left(
        cls, days_left: int
    ) -> Optional[Sequence[Bookings]]:
        tomorrow = date.today() + timedelta(days=days_left)
        query = select(Bookings).where(Bookings.date_from == tomorrow)
        async with AsyncSessionLocal() as session:
            result = await session.execute(query)
        return result.scalars().all()
