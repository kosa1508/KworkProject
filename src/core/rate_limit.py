from functools import wraps
from typing import Dict, Tuple, List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request

# Хранилище лимитов (в продакшене использовать Redis)
_rate_limit_storage: Dict[str, List[datetime]] = {}


def rate_limit(max_calls: int = 10, period: int = 3600):
    """
    Декоратор для rate limiting
    max_calls - максимальное количество вызовов
    period - период в секундах
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Получаем ключ (IP + endpoint)
            client_ip = request.client.host if request.client else "unknown"
            endpoint = request.url.path
            key = f"{client_ip}:{endpoint}"

            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=period)

            # Очищаем старые записи
            if key in _rate_limit_storage:
                _rate_limit_storage[key] = [
                    dt for dt in _rate_limit_storage[key]
                    if dt > cutoff
                ]
            else:
                _rate_limit_storage[key] = []

            # Проверяем лимит
            if len(_rate_limit_storage[key]) >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Limit: {max_calls} per {period} seconds"
                )

            # Добавляем текущий запрос
            _rate_limit_storage[key].append(now)

            # Вызываем функцию
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator