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
    'random-name': {
        'task': 'periodic_task',
        'schedule': 5, #seconds
        #'schedule': crontab(minute='30', hour='15'),
    }
}