# Базовый образ для сборки
FROM python:3.11-slim AS builder

WORKDIR /booking

# Установка зависимостей
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /booking/wheels -r requirements.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /booking

# Копирование собранных колес
COPY --from=builder /booking/wheels /wheels
COPY --from=builder /booking/requirements.txt .

# Установка зависимостей
RUN pip install --no-cache /wheels/*

# Копирование кода приложения
COPY . .

# Установка прав и очистка
RUN chmod +x entrypoint.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["./entrypoint.sh"]

# EXPOSE 8000
