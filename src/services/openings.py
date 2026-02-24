from datetime import datetime, timedelta
from typing import List, Optional
import hashlib

from src.exceptions import (
    ObjectNotFoundException,
    CaseNotFoundException,
    ItemNotFoundException,
    UserNotFoundException,
    InsufficientBalanceException,
)
from src.schemas.openings import (
    OpeningRequest,
    OpeningResponse,
    OpeningVerifyRequest,
    OpeningVerifyResponse,
    OpeningHistoryItem
)
from src.schemas.inventory import InventoryItem
from src.services.base import BaseService
from src.services.cases import CaseService
from src.services.items import ItemService
from src.services.users import UsersService
from src.services.rng import CryptoRNGService


class CaseOpeningService(BaseService):
    """
    Сервис для открытия кейсов с криптографическим RNG
    """

    # Лимиты на открытия
    RATE_LIMIT_OPENINGS = 10  # максимум открытий
    RATE_LIMIT_HOURS = 24  # за N часов

    async def open_case(
            self,
            user_id: int,
            request: OpeningRequest,
            client_ip: Optional[str] = None,
            user_agent: Optional[str] = None
    ) -> OpeningResponse:
        """
        Открывает кейс для пользователя
        """
        # 1. Проверяем idempotency ключ
        existing = await self.db.openings.get_by_idempotency_key(request.idempotency_key)
        if existing:
            # Если такое открытие уже было, возвращаем его результат
            return OpeningResponse.model_validate(existing)

        # 2. Проверяем rate limit
        openings_count = await self.db.openings.get_user_openings_count(
            user_id,
            hours=self.RATE_LIMIT_HOURS
        )
        if openings_count >= self.RATE_LIMIT_OPENINGS:
            raise RateLimitExceededException(
                f"Лимит открытий: максимум {self.RATE_LIMIT_OPENINGS} за {self.RATE_LIMIT_HOURS}ч"
            )

        # 3. Получаем информацию о кейсе
        case_service = CaseService(self.db)
        try:
            case = await case_service.get_case(request.case_id)
        except ObjectNotFoundException:
            raise CaseNotFoundException

        # 4. Проверяем баланс пользователя
        users_service = UsersService(self.db)
        user = await users_service.get_user_or_raise(user_id)

        if user.balance < case.price:
            raise InsufficientBalanceException

        # 5. Получаем все предметы кейса с весами
        items_service = ItemService(self.db)
        items = await items_service.get_case_items_with_weights(request.case_id)

        if not items:
            raise ItemNotFoundException

        # 6. Списываем деньги за кейс
        await users_service.decrease_balance(user_id, case.price)

        # 7. Генерируем криптостойкие сиды
        server_seed, server_seed_hash = CryptoRNGService.generate_server_seed()
        client_seed = CryptoRNGService.generate_client_seed()

        # 8. Получаем nonce (количество открытий пользователя)
        user_openings = await self.db.openings.get_user_openings_count(user_id, hours=24 * 30)
        nonce = user_openings + 1

        # 9. Генерируем roll
        roll = CryptoRNGService.generate_roll(server_seed, client_seed, nonce)

        # 10. Выбираем предмет
        items_dicts = [
            {
                'id': item.id,
                'name': item.name,
                'rarity': item.rarity,
                'base_price': item.base_price,
                'weight': item.weight
            }
            for item in items
        ]

        selected_item = CryptoRNGService.select_item_by_roll(roll, items_dicts)

        # 11. Обновляем статистику предмета
        await items_service.increment_open_count(selected_item['id'])

        # 12. Сохраняем информацию об открытии
        opening_data = {
            'user_id': user_id,
            'case_id': case.id,
            'item_id': selected_item['id'],
            'idempotency_key': request.idempotency_key,
            'server_seed': server_seed,
            'server_seed_hash': server_seed_hash,
            'client_seed': client_seed,
            'nonce': nonce,
            'roll': roll,
            'item_name': selected_item['name'],
            'item_rarity': selected_item['rarity'],
            'item_price': selected_item['base_price'],
            'client_ip': client_ip,
            'user_agent': user_agent
        }

        opening = await self.db.openings.add(opening_data)

        # 13. Добавляем предмет в инвентарь пользователя
        inventory_data = {
            'user_id': user_id,
            'opening_id': opening.id,
            'item_id': selected_item['id'],
            'item_name': selected_item['name'],
            'item_rarity': selected_item['rarity'],
            'item_price': selected_item['base_price']
        }

        await self.db.inventory.add(inventory_data)
        await self.db.commit()

        # 14. Формируем ответ (без серверного сида, только хеш)
        return OpeningResponse(
            id=opening.id,
            case_id=case.id,
            item_id=selected_item['id'],
            item_name=selected_item['name'],
            item_rarity=selected_item['rarity'],
            item_price=selected_item['base_price'],
            roll=roll,
            server_seed_hash=server_seed_hash,
            client_seed=client_seed,
            nonce=nonce,
            created_at=opening.created_at
        )

    async def get_user_history(
            self,
            user_id: int,
            limit: int = 20,
            offset: int = 0
    ) -> List[OpeningHistoryItem]:
        """
        Получает историю открытий пользователя
        """
        openings = await self.db.openings.get_user_openings(user_id, limit, offset)

        history = []
        for opening in openings:
            # Получаем информацию о кейсе
            case = await self.db.cases.get_one(id=opening.case_id)

            history.append(OpeningHistoryItem(
                id=opening.id,
                case_name=case.name,
                item_name=opening.item_name,
                item_rarity=opening.item_rarity,
                item_price=opening.item_price,
                created_at=opening.created_at
            ))

        return history

    async def verify_opening(
            self,
            user_id: int,
            request: OpeningVerifyRequest
    ) -> OpeningVerifyResponse:
        """
        Проверяет честность открытия кейса
        """
        # 1. Получаем открытие из БД
        opening = await self.db.openings.get_opening_by_id(request.opening_id, user_id)

        if not opening:
            return OpeningVerifyResponse(
                is_valid=False,
                expected_roll=0,
                expected_item=None
            )

        # 2. Проверяем, что сиды совпадают
        if (opening.server_seed != request.server_seed or
                opening.client_seed != request.client_seed or
                opening.nonce != request.nonce):
            return OpeningVerifyResponse(
                is_valid=False,
                expected_roll=opening.roll,
                expected_item=None
            )

        # 3. Проверяем хеш серверного сида
        calculated_hash = hashlib.sha256(request.server_seed.encode()).hexdigest()
        if calculated_hash != opening.server_seed_hash:
            return OpeningVerifyResponse(
                is_valid=False,
                expected_roll=opening.roll,
                expected_item=None
            )

        # 4. Проверяем roll
        is_valid = CryptoRNGService.verify_fairness(
            request.server_seed,
            request.client_seed,
            request.nonce,
            request.roll
        )

        # 5. Получаем ожидаемый предмет (для демонстрации)
        expected_item = None
        if is_valid:
            items = await self.db.items.get_all(case_id=opening.case_id)
            items_dicts = [
                {
                    'id': item.id,
                    'name': item.name,
                    'rarity': item.rarity,
                    'base_price': item.base_price,
                    'weight': item.weight
                }
                for item in items
            ]
            selected = CryptoRNGService.select_item_by_roll(request.roll, items_dicts)

            if selected:
                expected_item = {
                    'id': selected['id'],
                    'name': selected['name'],
                    'rarity': selected['rarity'],
                    'price': selected['base_price']
                }

        return OpeningVerifyResponse(
            is_valid=is_valid,
            expected_roll=opening.roll,
            expected_item=expected_item
        )

    async def get_opening_stats(self, case_id: int) -> dict:
        """
        Получает статистику открытий кейса
        """
        return await self.db.openings.get_case_stats(case_id)