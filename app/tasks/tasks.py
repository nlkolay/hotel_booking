# Обычные отложенные таски для селери.
# Нет обращений к бд, нет Алхимии, нет обхода асинхронности или смеси движков, как в scheduled.py
import smtplib
from pathlib import Path

from app.config import settings
from app.models import Bookings
from app.tasks.celery_app import celery
from app.tasks.email_templates import create_booking_confirmation_template
from PIL import Image
from pydantic import EmailStr


@celery.task
def process_pic(
    path: str,
):
    im_path = Path(path)
    im = Image.open(im_path)
    im_resized_1000_500 = im.resize((1000, 500))
    im_resized_200_100 = im.resize((200, 100))
    im_resized_1000_500.save(f"app/static/images/resized_1000_500_{im_path.name}")
    im_resized_200_100.save(f"app/static/images/resized_200_100_{im_path.name}")


@celery.task
def send_booking_confirmation_email(
    booking: Bookings,
    email_to: EmailStr,
):
    msg_content = create_booking_confirmation_template(booking, email_to)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
