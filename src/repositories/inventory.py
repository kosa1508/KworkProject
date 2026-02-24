from sqlalchemy import select, and_, update, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List

from src.models import UserInventoryOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import InventoryDataMapper


class InventoryRepository(BaseRepository):
    model = UserInventoryOrm
    mapper = InventoryDataMapper

    async def get_user_inventory(
            self,
            user_id: int,
            limit: int = 100,
            offset: int = 0
    ) -> List[UserInventoryOrm]:
        """Получить инвентарь пользователя"""
        query = (
            select(self.model)
            .filter_by(user_id=user_id, is_sold=False)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_opening_id(self, opening_id: int) -> Optional[UserInventoryOrm]:
        """Получить предмет по ID открытия"""
        query = select(self.model).filter_by(opening_id=opening_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def mark_as_sold(self, inventory_id: int, price: int):
        """Отметить предмет как проданный"""
        stmt = (
            update(self.model)
            .where(self.model.id == inventory_id)
            .values(
                is_sold=True,
                sold_price=price,
                sold_at=func.now()
            )
        )
        await self.session.execute(stmt)