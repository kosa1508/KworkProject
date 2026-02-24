from datetime import datetime
from typing import Optional, List

from src.exceptions import (
    ObjectNotFoundException,
    UserNotFoundException,
    InsufficientBalanceException
)
from src.schemas.users import User
from src.schemas.inventory import InventoryItem
from src.services.base import BaseService


class UsersService(BaseService):
    """
    Сервис для работы с пользователями
    """

    async def get_user_or_raise(self, user_id: int) -> User:
        """
        Получает пользователя по ID или выбрасывает исключение
        """
        try:
            return await self.db.users.get_one(id=user_id)
        except ObjectNotFoundException:
            raise UserNotFoundException

    async def decrease_balance(self, user_id: int, amount: int):
        """
        Уменьшает баланс пользователя
        """
        user = await self.get_user_or_raise(user_id)

        if user.balance < amount:
            raise InsufficientBalanceException

        new_balance = user.balance - amount
        await self.db.users.edit({'balance': new_balance}, id=user_id)
        await self.db.commit()

        return new_balance

    async def increase_balance(self, user_id: int, amount: int):
        """
        Увеличивает баланс пользователя
        """
        user = await self.get_user_or_raise(user_id)

        new_balance = user.balance + amount
        await self.db.users.edit({'balance': new_balance}, id=user_id)
        await self.db.commit()

        return new_balance

    async def get_user_inventory(
            self,
            user_id: int,
            limit: int = 100,
            offset: int = 0
    ) -> List[InventoryItem]:
        """
        Получает инвентарь пользователя
        """
        return await self.db.inventory.get_user_inventory(user_id, limit, offset)

    async def sell_item(self, user_id: int, inventory_id: int, price: int) -> InventoryItem:
        """
        Продает предмет из инвентаря
        """
        # Получаем предмет
        inventory = await self.db.inventory.get_one(id=inventory_id, user_id=user_id)

        if not inventory:
            raise ObjectNotFoundException("Предмет не найден")

        if inventory.is_sold:
            raise ValueError("Предмет уже продан")

        # Помечаем как проданный
        await self.db.inventory.mark_as_sold(inventory_id, price)

        # Начисляем деньги
        await self.increase_balance(user_id, price)

        return await self.db.inventory.get_one(id=inventory_id)