import time
import hashlib
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AttemptData:
    """Данные о попытках входа"""
    count: int = 0
    first_attempt: float = 0.0
    blocked_until: Optional[float] = None


class RateLimiter:
    """
    Rate limiter для защиты от брутфорса
    Хранит попытки входа в памяти
    """

    def __init__(self):
        # Структура: {key: AttemptData}
        self.attempts: Dict[str, AttemptData] = {}

        # Настройки по умолчанию
        self.default_config = {
            "max_attempts": 10,
            "window_seconds": 300,  # 5 минут
            "block_seconds": 900  # 15 минут
        }

        # Конфигурация для разных действий
        self.action_configs = {
            "login": {
                "max_attempts": 10,
                "window_seconds": 300,
                "block_seconds": 900
            },
            "register": {
                "max_attempts": 5,  # Для регистрации меньше попыток
                "window_seconds": 300,
                "block_seconds": 900
            }
        }

    def _get_config(self, action: str = "default") -> dict:
        """Получает конфигурацию для действия"""
        if action in self.action_configs:
            return self.action_configs[action]
        return self.default_config

    def _get_key(self, ip: str, email: str, action: str = "default") -> str:
        """Создает уникальный ключ на основе IP, email и действия"""
        key_data = f"{ip}:{email}:{action}".encode()
        return hashlib.sha256(key_data).hexdigest()

    async def is_allowed(self, ip: str, email: str, action: str = "default") -> Tuple[bool, Optional[int]]:
        """
        Проверяет, разрешен ли запрос
        Возвращает (разрешено, сколько секунд осталось до разблокировки)
        """
        config = self._get_config(action)
        key = self._get_key(ip, email, action)
        now = time.time()

        # Получаем данные о попытках
        data = self.attempts.get(key, AttemptData())

        # Проверяем, не заблокирован ли
        if data.blocked_until and now < data.blocked_until:
            retry_after = int(data.blocked_until - now)
            return False, retry_after

        # Если блокировка истекла, сбрасываем
        if data.blocked_until and now >= data.blocked_until:
            data = AttemptData()
            self.attempts[key] = data

        # Если окно попыток истекло, сбрасываем счетчик
        if data.count > 0 and (now - data.first_attempt) > config["window_seconds"]:
            data = AttemptData()
            self.attempts[key] = data

        return True, None

    async def add_attempt(self, ip: str, email: str, action: str = "default") -> Tuple[bool, Optional[int]]:
        """
        Добавляет неудачную попытку
        Возвращает (не заблокирован ли, сколько секунд до разблокировки)
        """
        config = self._get_config(action)
        key = self._get_key(ip, email, action)
        now = time.time()

        # Получаем или создаем данные
        if key not in self.attempts:
            self.attempts[key] = AttemptData(first_attempt=now, count=1)
        else:
            data = self.attempts[key]

            # Проверяем, не истекло ли окно
            if (now - data.first_attempt) > config["window_seconds"]:
                # Новое окно
                data.count = 1
                data.first_attempt = now
                data.blocked_until = None
            else:
                # Увеличиваем счетчик в текущем окне
                data.count += 1

                # Проверяем, не превышен ли лимит
                if data.count >= config["max_attempts"]:
                    data.blocked_until = now + config["block_seconds"]
                    self.attempts[key] = data
                    return False, config["block_seconds"]

            self.attempts[key] = data

        # Проверяем, не заблокирован ли после добавления
        if self.attempts[key].blocked_until:
            retry_after = int(self.attempts[key].blocked_until - now)
            return False, retry_after

        return True, None

    async def reset_attempts(self, ip: str, email: str, action: str = "default"):
        """Сбрасывает счетчик попыток после успешного действия"""
        key = self._get_key(ip, email, action)
        if key in self.attempts:
            del self.attempts[key]

    async def get_attempts(self, ip: str, email: str, action: str = "default") -> int:
        """Возвращает количество текущих попыток"""
        config = self._get_config(action)
        key = self._get_key(ip, email, action)
        data = self.attempts.get(key, AttemptData())

        # Проверяем, не истекло ли окно
        now = time.time()
        if data.count > 0 and (now - data.first_attempt) > config["window_seconds"]:
            return 0

        return data.count


# Создаем глобальный экземпляр
rate_limiter = RateLimiter()