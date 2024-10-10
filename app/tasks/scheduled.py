from app.tasks.celery_app import celery


@celery.task(name='periodic_task')
def periodic_task():
    print('smth...')