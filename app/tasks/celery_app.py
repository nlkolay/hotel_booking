# Конфиг для селери и расписание бита
from app.config import settings
from celery import Celery

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["app.tasks.tasks", "app.tasks.scheduled"],
)

celery.conf.beat_schedule = {
    "send-3-days-reminder": {
        "task": "days-left-reminder",
        "args": (3,),
        'schedule': '0 18 * * *',  # Every day at
        # "schedule": 5,  # seconds
        #'schedule': crontab(minute=30, hour=15),
    },
    "send-1-day-reminder": {
        "task": "days-left-reminder",
        "args": (1,),
        'schedule': '0 18 * * *',  # Every day at
        # "schedule": 5,  # seconds
        #'schedule': crontab(minute=0, hour=9),
    },
}
celery.conf.timezone = "UTC"  # or any other timezone you need
