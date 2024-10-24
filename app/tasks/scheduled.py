# Таски по расписанию для селери бит. 
# Из-за наличия обращений к бд необходим обход асинхронности или смеси движков, которые ломают Алхимию.
import asyncio
from os.path import isfile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.tasks.dao import TaskDAO
from app.tasks.celery_app import celery
from app.tasks.email_templates import create_booking_reminder_template
from app.config import settings

# Настройка базы данных
DATABASE_URL = settings.DATABASE_URL  # Замените на вашу строку подключения
engine = create_async_engine(DATABASE_URL)#, poolclass=NullPool) при новых ошибках (см внизу)
#Session = async_sessionmaker(engine)

@celery.task(name='days-left-reminder')
def periodic_task(days_left: int): # Обход синхронности селери
    loop = asyncio.get_event_loop()  # Get the current event loop
    loop.run_until_complete(run_periodic_task(days_left))  # Run the task on the current loop

async def run_periodic_task(days_left: int):  
    async with AsyncSession(engine) as session:
        # Получаем пользователей с запланированным заездом на завтра
        task_dao = TaskDAO(session)
        bookings = await task_dao.get_booking_by_days_left(days_left)
        for booking in bookings:
            path = f'app/tmp/{booking.id}.eml'
            if not (isfile(path)):
                with open(f'app/tmp/{booking.id}.eml', 'wb') as f:
                    email_to = await task_dao.get_email_by_booking(booking)
                    msg_content = create_booking_reminder_template(booking, email_to)
                    f.write(msg_content)

""" Как правильно получать ответ в таске, если нужно обращаться к БД и в ответ приходит корутина?

Добавил движок с параметром NullPool:

DATABASE_PARAMS = {"poolclass": NullPool}
engine_nullpool = create_async_engine(settings.DATABASE_URL, **DATABASE_PARAMS)
async_session_maker_nullpool = sessionmaker(engine_nullpool, class_=AsyncSession, expire_on_commit=False)

В методе класса DAO заменил на него:

async with async_session_maker_nullpool() as session:

остальное там не трогал.

Сама таска синхронная, разумеется вызвать через await асинхронный метод класса нельзя, поэтому запускаю теперь через asyncio.run() так:

users = asyncio.run(BookingDAO.get_bookings_by_date_from(day_to_enter))

Оно работает, но сдается мне, что где то подвох. В комментарии на прошлом шаге написано, что с asyncio.run  будут проблемы, но теперь движок с NullPool. Этого достаточно или вообще все не так?
 """