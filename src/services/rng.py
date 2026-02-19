import hashlib
import hmac
import secrets
import random
from typing import Tuple, List, Dict, Any


class CryptoRNGService:
    """
    Криптографически безопасный генератор случайных чисел для открытия кейсов
    Основан на HMAC-SHA256 с доказуемо честной системой
    """

    @staticmethod
    def generate_server_seed() -> str:
        """Генерирует криптостойкий серверный сид (64 символа hex)"""
        return secrets.token_hex(32)

    @staticmethod
    def generate_client_seed() -> str:
        """Генерирует криптостойкий клиентский сид"""
        return secrets.token_hex(16)

    @staticmethod
    def hash_server_seed(server_seed: str) -> str:
        """Хэширует серверный сид для публикации до открытия"""
        return hashlib.sha256(server_seed.encode()).hexdigest()

    @staticmethod
    def generate_roll(
            server_seed: str,
            client_seed: str,
            nonce: int,
            max_value: int = 1_000_000
    ) -> int:
        """
        Генерирует число от 0 до max_value-1 (по умолчанию 0-999999)
        Использует HMAC-SHA256 для криптостойкости
        """
        message = f"{client_seed}:{nonce}".encode()
        hmac_obj = hmac.new(
            server_seed.encode(),
            message,
            hashlib.sha256
        )
        hex_digest = hmac_obj.hexdigest()

        # Берем первые 8 символов hex (32 бита) и конвертируем в int
        roll_int = int(hex_digest[:8], 16)

        return roll_int % max_value

    @staticmethod
    def select_item_by_roll(
            roll: int,
            items: List[Dict[str, Any]],
            max_roll: int = 1_000_000
    ) -> Dict[str, Any]:
        """
        Выбирает предмет на основе roll с учетом редкости
        rarity: 1 (очень редкий) - 10 (обычный)
        """
        if not items:
            return None

        # Сортируем предметы по редкости (от редких к обычным)
        sorted_items = sorted(items, key=lambda x: x['rarity'], reverse=True)

        # Распределяем шансы на основе rarity
        # rarity 10 = 50% шанс, rarity 5 = 25% шанс, rarity 1 = 2% шанс и т.д.
        total_weight = 0
        weighted_items = []

        for item in sorted_items:
            # Вес = rarity^2 (можно настроить)
            weight = item['rarity'] ** 2
            weighted_items.append({
                'item': item,
                'weight': weight,
                'min_range': total_weight,
                'max_range': total_weight + weight
            })
            total_weight += weight

        # Нормализуем roll к диапазону весов
        normalized_roll = (roll / max_roll) * total_weight

        # Выбираем предмет
        for weighted_item in weighted_items:
            if weighted_item['min_range'] <= normalized_roll < weighted_item['max_range']:
                return weighted_item['item']

        # Если ничего не выбрали (погрешность), возвращаем последний (самый частый)
        return weighted_items[-1]['item'] if weighted_items else None

    @staticmethod
    def verify_fairness(
            server_seed: str,
            client_seed: str,
            nonce: int,
            claimed_roll: int
    ) -> bool:
        """
        Проверяет честность открытия
        Клиент может проверить, что сервер не мухлевал
        """
        calculated_roll = CryptoRNGService.generate_roll(
            server_seed, client_seed, nonce
        )
        return calculated_roll == claimed_roll