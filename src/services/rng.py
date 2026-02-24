import hashlib
import hmac
import secrets
from typing import List, Dict, Any, Tuple


class CryptoRNGService:
    """
    Криптографически безопасный генератор случайных чисел
    Использует HMAC-SHA256 для доказуемо честной системы
    """

    @staticmethod
    def generate_server_seed() -> Tuple[str, str]:
        """
        Генерирует серверный сид и его хеш
        Возвращает: (seed, seed_hash)
        """
        seed = secrets.token_hex(32)
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        return seed, seed_hash

    @staticmethod
    def generate_client_seed() -> str:
        """Генерирует клиентский сид"""
        return secrets.token_hex(16)

    @staticmethod
    def generate_idempotency_key() -> str:
        """Генерирует ключ идемпотентности"""
        return secrets.token_hex(32)

    @staticmethod
    def generate_roll(
            server_seed: str,
            client_seed: str,
            nonce: int,
            max_value: int = 1_000_000
    ) -> int:
        """
        Генерирует число от 0 до max_value-1
        Использует HMAC-SHA256 для криптостойкости
        """
        message = f"{client_seed}:{nonce}".encode()
        hmac_obj = hmac.new(
            server_seed.encode(),
            message,
            hashlib.sha256
        )
        hex_digest = hmac_obj.hexdigest()

        # Берем первые 8 символов hex (32 бита)
        roll_int = int(hex_digest[:8], 16)

        return roll_int % max_value

    @staticmethod
    def select_item_by_roll(
            roll: int,
            items: List[Dict[str, Any]],
            max_roll: int = 1_000_000
    ) -> Dict[str, Any]:
        """
        Выбирает предмет на основе roll с учетом весов
        """
        if not items:
            return None

        # Сортируем по весу (для последовательности)
        sorted_items = sorted(items, key=lambda x: x['weight'], reverse=True)

        # Вычисляем общий вес
        total_weight = sum(item['weight'] for item in sorted_items)

        # Нормализуем roll к диапазону весов
        normalized_roll = (roll / max_roll) * total_weight

        # Выбираем предмет
        cumulative = 0
        for item in sorted_items:
            cumulative += item['weight']
            if normalized_roll < cumulative:
                return item

        # На случай погрешности - возвращаем последний
        return sorted_items[-1] if sorted_items else None

    @staticmethod
    def calculate_item_chances(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Рассчитывает шансы выпадения для каждого предмета в процентах
        """
        if not items:
            return []

        total_weight = sum(item['weight'] for item in items)

        result = []
        for item in items:
            item_copy = item.copy()
            item_copy['chance_percent'] = (item['weight'] / total_weight) * 100
            result.append(item_copy)

        return result

    @staticmethod
    def verify_fairness(
            server_seed: str,
            client_seed: str,
            nonce: int,
            claimed_roll: int
    ) -> bool:
        """
        Проверяет честность открытия
        """
        calculated_roll = CryptoRNGService.generate_roll(
            server_seed, client_seed, nonce
        )
        return calculated_roll == claimed_roll