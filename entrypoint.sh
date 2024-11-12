#!/bin/sh

# Ожидание запуска базы данных
python wait_for_postgres.py

# Выполнение миграций
alembic upgrade head

# Запуск приложения
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
