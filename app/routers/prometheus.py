import time
from random import random

from fastapi import APIRouter, Depends, HTTPException
from prometheus_client import Counter, Histogram

from app.dependencies import get_current_user_role

router = APIRouter(
    prefix="/prometheus",
    tags=["Тестирование Grafana + Prometheus"]
)

# Определение метрик Prometheus
request_counter = Counter('request_count', 'Total number of requests')
error_counter = Counter('error_count', 'Total number of errors')
response_time_histogram = Histogram('response_time', 'Response time in seconds')

@router.get("/get_error")
async def get_error(
    current_user_role = Depends(get_current_user_role),
):
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав.")
    request_counter.inc()  # Увеличиваем счетчик запросов
    if random() > 0.5:
        error_counter.inc()  # Увеличиваем счетчик ошибок
        raise ZeroDivisionError("Division by zero error")
    else:
        error_counter.inc()  # Увеличиваем счетчик ошибок
        raise KeyError("Key error")

# @router.get("/time_consumer")
# @response_time_histogram.time()  # Измеряем время выполнения
# async def time_consumer(
#     current_user_role = Depends(get_current_user_role),
# ):
#     if current_user_role != "admin":
#         raise HTTPException(status_code=403, detail="Недостаточно прав.")
#     request_counter.inc()  # Увеличиваем счетчик запросов
#     time.sleep(random() * 5)
#     return {"result": 1}

@router.get("/memory_consumer")
async def memory_consumer(
    current_user_role = Depends(get_current_user_role),
):
    if current_user_role != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав.")
    request_counter.inc()  # Увеличиваем счетчик запросов
    _ = [i for i in range(30_000_000)]
    return {"result": 1}
