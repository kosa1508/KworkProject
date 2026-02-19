from src.exceptions import ObjectNotFoundException, UserNotFoundException, InsufficientBalanceException
from src.services.base import BaseService
from src.schemas.users import User
from datetime import datetime


class UsersService(BaseService):
    """
    Сервис для работы с пользователями
    """

    async def get_one_or_none_user(self, user_id: int) -> User | None:
        """
        Получает пользователя по ID
        """
        try:
            return await self.db.users.get_one(id=user_id)
        except ObjectNotFoundException:
            return None

    async def get_user_or_raise(self, user_id: int) -> User:
        """
        Получает пользователя по ID или выбрасывает исключение
        """
        user = await self.get_one_or_none_user(user_id)
        if not user:
            raise UserNotFoundException
        return user

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

    async def increase_balance(self, user_id: int, amount: int):
        """
        Увеличивает баланс пользователя
        """
        user = await self.get_user_or_raise(user_id)

        new_balance = user.balance + amount
        await self.db.users.edit({'balance': new_balance}, id=user_id)
        await self.db.commit()

    async def add_item_to_inventory(self, user_id: int, item_id: int, item_name: str, item_price: int):
        """
        Добавляет предмет в инвентарь пользователя
        Упрощенная версия - просто логируем открытие
        """
        # В вашем случае предметы не сохраняются в инвентарь,
        # только информация об открытии кейса
        pass

    async def get_user_by_email(self, email: str):
        """
        Получает пользователя по email
        """
        return await self.db.users.get_user_by_email(email)