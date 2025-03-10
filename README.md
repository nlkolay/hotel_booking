# Hotel Booking FastAPI App "Bronenosets"

Асинхронное приложение Fastapi для бронирования гостиничных номеров. 
Стэк: PostgreSQL, Pydantic, SQLAlchemy, и JWT authentication.

Запуск в терминале (dev):
uvicorn app.main:app --reload

Для чего нужен каждый из файлов:

    main — файл с конфигурацией FastAPI приложения. В нем задается само приложение, его жизненный цикл (lifespan) — определяет, какие команды должны быть запущены до старта приложения, какие — перед закрытием. В файл main импортируются все роутеры из разных уголков приложения. Опционально добавляется версионирование. В этом же файле иногда пишут команду  uvicorn.run(...), где указана конфигурация для запуска uvicorn'а (порт, режим дебага и пр. — мы в курсе так не делали). Из этого файла ничего не импортируется, только он импортирует объекты из других файлов
    database — файл с конфигурацией базы данных. Здесь создается пул подключений к базе через engine = create_async_engine(...), задается кол-во соединений в пуле, создаются фабрики сессий (async_sessionamaker). Из этого файла затем импортируется фабрика сессий для работы с базой данных
    config — содержит объект, в котором хранятся распарсенные переменные окружения. Мы используем Pydantic Settings для этой цели. Можно использовать python-dotenv, но тогда не будет валидации данных
    dao/base — базовый интерфейс по работе с таблицей в базе данных. Реализует CRUD, если по-простому: позволяет получать, изменять, добавлять, удалять объекты из конкретной таблицы. Так как эти команды очень часто нужны на проекте, они выносятся в базовый класс BaseDAO/BaseRepository
    Router — обычно роутеров много в приложении, каждый под свою часть приложения. В файле router.py обычно хранится набор эндпоинтов/ручек, с которыми в итоге будет взаимодействовать клиент (фронтенд или другой бэкенд).
    DAO — содержит класс, наследующийся от BaseDAO/BaseRepository, и реализующий свой уникальный набор методов по работе с таблицей или набором таблиц в базе данных, которые не подходят под уже имеющиеся в BaseDAO команды. Обычно в таких функциях присутствует дополнительная бизнес-логика: если в таблице N у юзера больше X товаров, то вставь в таблицу Y запись Z, иначе вставь запись W
    schemas — Pydantic модели/схемы, описывающие используемые наборы данных. Часто под одну таблицу делается несколько моделей: как минимум одна модель для POST запроса (в ней отсутствует поле id, которое задается базой данных), и вся модель целиком — отражает данные, получаемые клиентом при GET запросе. Хотя часто клиенту не нужно все столбцы из таблицы, поэтому количество моделей соответствует количеству разных ее вариаций внутри приложения
    models — файл с моделями SQLAlchemy, которые отражают реальные таблицы в базе данных. Модели нужны нам, чтобы мы могли писать запросы без использования сырого SQL, а писать в более питонячем стиле, используя классы и оперируя их атрибутами и методами. Модели затем используются в файлах DAO

Взаимосвязи файлов в проекте
main.py: Файл главного приложения, который объединяет все части приложения, включая базы данных, маршрутизацию и зависимости. Этот файл инициализирует FastAPI и подключает все маршруты, определенные в routers.

database.py: Отвечает за установление соединения с базой данных и создание сессий доступа. Он используется в dependencies.py и dao.py для управления операциями базы данных.

models.py: Определяет структуру таблиц базы данных, используемую в dao.py и crud.py для выполнения операций с данными.

schemas.py: Определяет схемы для валидации данных, используемые в маршрутах (например, auth.py, bookings.py) для проверки входных и выходных данных.
crud.py и dao.py: Содержат функции и классы для доступа и управления данными в базе данных, используемые в маршрутах для обработки запросов пользователей.

dependencies.py: Содержит зависимости и вспомогательные функции для аутентификации и авторизации, используемые для защиты маршрутов.

utils.py: Содержит различные вспомогательные функции, такие как хэширование паролей и валидация email, используемые в dependencies.py и routers.

config.py: Обеспечивает централизованное управление переменными окружения и их валидацией. Используется во всех модулях, где необходимы конфигурации, например в database.py, dependencies.py.

routers/: Содержит файлы с маршрутами для различных частей приложения. Эти файлы подключаются к FastAPI через main.py:
auth.py: Маршруты для аутентификации и авторизации.
hotels.py: Маршруты для работы с отелями.
rooms.py: Маршруты для работы с комнатами в отелях.
bookings.py: Маршруты для управления бронированиями.

alembic/ и alembic.ini: Отвечают за управление миграциями базы данных, обеспечивая поддержку актуальной схемы базы данных.

Заключение
Этот проект организован по стандартным принципам архитектуры FastAPI, что делает его легко поддерживаемым и масштабируемым. Каждая часть проекта выполняет свою четко определенную роль, и все зависимости инжектируются через функции и классы, что облегчает тестирование и модульное использование различных компонентов.
