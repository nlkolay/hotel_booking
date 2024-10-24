from datetime import date, timedelta
from typing import Optional, Sequence
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Bookings, Users

class TaskDAO:
    def __init__(self, session: Session):
        self.session = session

    async def get_email_by_booking(self, booking: Bookings)  -> EmailStr:
        query = select(Users.email).where(Users.id == booking.user_id)
        email = await self.session.execute(query)
        return email.scalar_one_or_none()
    
    async def get_booking_by_days_left(self, days_left: int) -> Optional[Sequence[Bookings]]:
        tomorrow = date.today() + timedelta(days = days_left)
        query = select(Bookings).where(Bookings.date_from == tomorrow)
        result = await self.session.execute(query)
        return result.scalars().all()