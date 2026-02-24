from datetime import datetime
from typing import List, Optional

from src.exceptions import ObjectNotFoundException, ItemNotFoundException
from src.schemas.items import ItemCreate, ItemUpdate, Item
from src.services.base import BaseService


class ItemService(BaseService):

    async def get_case_items(self, case_id: int, only_active: bool = True) -> List[Item]:
        """Получить все предметы кейса"""
        filters = {'case_id': case_id}
        if only_active:
            filters['is_active'] = True

        return await self.db.items.get_all(order_by='-rarity', **filters)

    async def get_case_items_with_weights(self, case_id: int) -> List[Item]:
        """Получить предметы кейса с весами для рандома"""
        items = await self.get_case_items(case_id)

        # Добавляем вес каждому предмету
        for item in items:
            # Вес может быть настроен через админку
            # По умолчанию используем rarity^2 * 10
            if not hasattr(item, 'weight') or not item.weight:
                item.weight = (item.rarity ** 2) * 10

        return items

    async def increment_open_count(self, item_id: int):
        """Увеличить счетчик открытий предмета"""
        item = await self.get_item(item_id)

        update_data = {
            'total_opened': item.total_opened + 1,
            'last_opened_at': datetime.utcnow()
        }

        await self.db.items.edit(update_data, id=item_id)
        await self.db.commit()

    async def get_item(self, item_id: int) -> Item:
        """Получить предмет по ID"""
        try:
            return await self.db.items.get_one(id=item_id)
        except ObjectNotFoundException:
            raise ItemNotFoundException

    async def create_item(self, case_id: int, data: ItemCreate) -> Item:
        """Создать предмет"""
        item_data = data.model_dump()
        item_data['case_id'] = case_id

        item = await self.db.items.add(item_data)
        await self.db.commit()
        return item

    async def update_item(self, item_id: int, data: ItemUpdate) -> Item:
        """Обновить предмет"""
        await self.get_item(item_id)

        update_data = data.model_dump(exclude_unset=True)
        await self.db.items.edit(update_data, id=item_id)
        await self.db.commit()

        return await self.get_item(item_id)

    async def delete_item(self, item_id: int):
        """Удалить предмет (мягкое удаление)"""
        await self.update_item(item_id, ItemUpdate(is_active=False))