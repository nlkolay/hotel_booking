from email.message import EmailMessage

from app.config import settings
from app.models import Bookings
from pydantic import EmailStr


def create_booking_confirmation_template(
    booking: Bookings,
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Подтверждение бронирования</h1>
            Вы забронировали комнату в отеле с {booking.date_from} по {booking.date_to}.
        """,
        subtype="html",
    )

    result = email.as_bytes()

    return result


def create_booking_reminder_template(
    booking: Bookings,
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Напоминание о бронировании отеля"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Напоминание о бронировании отеля</h1>
            Не забывайте, что Вы забронировали комнату в отеле с {booking.date_from} по {booking.date_to}.
            Счастливого пребывания!
        """,
        subtype="html",
    )

    result = email.as_bytes()

    return result
