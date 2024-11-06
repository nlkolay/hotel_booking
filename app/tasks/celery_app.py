# Конфиг для селери и расписание бита
from celery import Celery

from app.config import settings


celery = Celery(
    'tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
    include=[
            'app.tasks.tasks',
            'app.tasks.scheduled'
            ]
)

celery.conf.beat_schedule ={
    'send-3-days-reminder': {
        'task': 'days-left-reminder',
        'args': (3,),
        'schedule': 5, #seconds
        #'schedule': crontab(minute=30, hour=15),
    },
    'send-1-day-reminder': {
        'task': 'days-left-reminder',
        'args': (1,),
        #'schedule': '0 9 * * *',  # Every day at 9 AM
        'schedule': 5, #seconds
        #'schedule': crontab(minute=0, hour=9),
    },
    'send-1-day-reminder': {
        'task': 'days-left-reminder',
        'args': (1,),
        #'schedule': '0 9 * * *',  # Every day at 9 AM
        'schedule': 5, #seconds
        #'schedule': crontab(minute=0, hour=9),
    },
    'send-1-day-reminder': {
        'task': 'days-left-reminder',
        'args': (3,),
        #'schedule': '0 9 * * *',  # Every day at 9 AM
        'schedule': 5, #seconds
        #'schedule': crontab(minute=0, hour=9),
    },
    'send-1-day-reminder': {
        'task': 'days-left-reminder',
        'args': (1,),
        #'schedule': '0 9 * * *',  # Every day at 9 AM
        'schedule': 5, #seconds
        #'schedule': crontab(minute=0, hour=9),
    },
}
celery.conf.timezone = 'UTC'  # or any other timezone you need
