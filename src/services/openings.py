from datetime import datetime
from typing import List, Dict, Any

from src.exceptions import (
    ObjectNotFoundException,
    CaseNotFoundException,
    ItemNotFoundException
)
from src.schemas.openings import (
    CaseOpeningRequest,
    CaseOpeningResponse,
    VerifyOpeningResponse
)
from src.services.base import BaseService
from src.services.cases import CaseService
from src.services.items import ItemService
from src.services.rng import CryptoRNGService
from src.services.users import UsersService


class CaseOpeningService(BaseService):
    """
    Сервис для открытия кейсов с криптографическим RNG
    """

    async def open_case(
            self,
            user_id: int,
            request: CaseOpeningRequest
    ) -> CaseOpeningResponse:
        """
        Открывает кейс для пользователя
        Весь рандом строго на сервере с криптостойким RNG
        """
        # 1. Получаем информацию о кейсе
        case_service = CaseService(self.db)
        try:
            case = await case_service.get_case(request.case_id)
        except ObjectNotFoundException:
            raise CaseNotFoundException

        # 2. Проверяем баланс пользователя
        users_service = UsersService(self.db)
        user = await users_service.get_one_or_none_user(user_id)

        if user.balance < case.price:
            raise InsufficientBalanceException

        # 3. Списываем деньги за кейс
        await users_service.decrease_balance(user_id, case.price)

        # 4. Получаем все предметы кейса
        items_service = ItemService(self.db)
        items = await items_service.get_case_items_with_weights(request.case_id)

        if not items:
            raise ItemNotFoundException

        # 5. Генерируем криптостойкие сиды
        server_seed = CryptoRNGService.generate_server_seed()
        client_seed = CryptoRNGService.generate_client_seed()

        # 6. Получаем следующий nonce для пользователя
        # (в реальном проекте храните nonce в БД для каждого пользователя/кейса)
        openings_count = await self.db.openings.get_user_openings_count(user_id)
        nonce = openings_count + 1

        # 7. Генерируем roll (0-999999)
        roll = CryptoRNGService.generate_roll(server_seed, client_seed, nonce)

        # 8. Выбираем предмет на основе roll
        selected_item = CryptoRNGService.select_item_by_roll(roll, items)

        # 9. Добавляем предмет в инвентарь пользователя
        await users_service.add_item_to_inventory(
            user_id=user_id,
            item_id=selected_item['id'],
            item_name=selected_item['name'],
            item_price=selected_item['base_price']
        )

        # 10. Сохраняем информацию об открытии
        opening_data = {
            'user_id': user_id,
            'case_id': case.id,
            'item_id': selected_item['id'],
            'server_seed': server_seed,
            'client_seed': client_seed,
            'nonce': nonce,
            'roll': roll,
            'created_at': datetime.utcnow()
        }

        opening = await self.db.openings.add(opening_data)
        await self.db.commit()

        # 11. Формируем ответ
        return CaseOpeningResponse(
            id=opening.id,
            user_id=user_id,
            case_id=case.id,
            item_id=selected_item['id'],
            item_name=selected_item['name'],
            item_rarity=selected_item['rarity'],
            item_price=selected_item['base_price'],
            server_seed=server_seed,
            client_seed=client_seed,
            nonce=nonce,
            roll=roll,
            created_at=opening.created_at
        )

    async def get_user_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Получает историю открытий пользователя
        """
        openings = await self.db.openings.get_user_openings(user_id, limit)

        history = []
        for opening in openings:
            # Получаем информацию о кейсе и предмете
            case = await self.db.cases.get_one(id=opening.case_id)
            item = await self.db.items.get_one(id=opening.item_id)

            history.append({
                'id': opening.id,
                'case_name': case.name,
                'item_name': item.name,
                'item_rarity': item.rarity,
                'item_price': item.base_price,
                'created_at': opening.created_at
            })

        return history

    async def verify_opening(
            self,
            user_id: int,
            opening_id: int,
            server_seed: str,
            client_seed: str,
            nonce: int,
            roll: int
    ) -> VerifyOpeningResponse:
        """
        Проверяет честность открытия кейса
        """
        # 1. Получаем открытие из БД
        opening = await self.db.openings.get_opening_by_id(opening_id, user_id)

        if not opening:
            return VerifyOpeningResponse(
                is_valid=False,
                expected_roll=0,
                expected_item=None
            )

        # 2. Проверяем, что сиды совпадают с теми, что были использованы
        if (opening.server_seed != server_seed or
                opening.client_seed != client_seed or
                opening.nonce != nonce):
            return VerifyOpeningResponse(
                is_valid=False,
                expected_roll=opening.roll,
                expected_item=None
            )

        # 3. Проверяем roll
        is_valid = CryptoRNGService.verify_fairness(
            server_seed, client_seed, nonce, roll
        )

        # 4. Получаем ожидаемый предмет
        expected_item = None
        if is_valid:
            items = await self.db.items.get_all(case_id=opening.case_id)
            selected_item = CryptoRNGService.select_item_by_roll(roll, items)
            expected_item = {
                'id': selected_item['id'],
                'name': selected_item['name'],
                'rarity': selected_item['rarity'],
                'price': selected_item['base_price']
            }

        return VerifyOpeningResponse(
            is_valid=is_valid,
            expected_roll=opening.roll,
            expected_item=expected_item
        )