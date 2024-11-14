import time
from random import random

from fastapi import APIRouter
from prometheus_client import Counter, Histogram

router = APIRouter(
    prefix="/prometheus",
    tags=["Тестирование Grafana + Prometheus"]
)

# Определение метрик Prometheus
request_counter = Counter('request_count', 'Total number of requests')
error_counter = Counter('error_count', 'Total number of errors')
response_time_histogram = Histogram('response_time', 'Response time in seconds')

@router.get("/get_error")
def get_error():
    request_counter.inc()  # Увеличиваем счетчик запросов
    if random() > 0.5:
        error_counter.inc()  # Увеличиваем счетчик ошибок
        raise ZeroDivisionError("Division by zero error")
    else:
        error_counter.inc()  # Увеличиваем счетчик ошибок
        raise KeyError("Key error")

@router.get("/time_consumer")
@response_time_histogram.time()  # Измеряем время выполнения
def time_consumer():
    request_counter.inc()  # Увеличиваем счетчик запросов
    time.sleep(random() * 5)
    return {"result": 1}

@router.get("/memory_consumer")
def memory_consumer():
    request_counter.inc()  # Увеличиваем счетчик запросов
    _ = [i for i in range(30_000_000)]
    return {"result": 1}
