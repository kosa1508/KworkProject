from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional, List

from src.models import CaseOpeningsOrm, CasesOrm, ItemsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CaseOpeningDataMapper


class CaseOpeningsRepository(BaseRepository):
    model = CaseOpeningsOrm
    mapper = CaseOpeningDataMapper

    async def get_by_idempotency_key(self, key: str) -> Optional[CaseOpeningsOrm]:
        """Получить открытие по idempotency ключу"""
        query = select(self.model).filter_by(idempotency_key=key)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_openings(
            self,
            user_id: int,
            limit: int = 50,
            offset: int = 0
    ) -> List[CaseOpeningsOrm]:
        """Получить историю открытий пользователя"""
        query = (
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_openings_count(self, user_id: int, hours: int = 24) -> int:
        """Получить количество открытий пользователя за последние N часов"""
        time_limit = datetime.utcnow() - timedelta(hours=hours)

        query = select(func.count()).where(
            and_(
                self.model.user_id == user_id,
                self.model.created_at >= time_limit
            )
        )
        result = await self.session.execute(query)
        return result.scalar()

    async def get_case_stats(self, case_id: int) -> dict:
        """Получить статистику открытий кейса"""
        # Общее количество открытий
        total_query = select(func.count()).where(self.model.case_id == case_id)
        total = await self.session.execute(total_query)

        # Суммарная стоимость
        value_query = select(func.sum(self.model.item_price)).where(self.model.case_id == case_id)
        total_value = await self.session.execute(value_query)

        # Статистика по предметам
        items_stats = (
            select(
                self.model.item_id,
                func.count().label('count'),
                func.avg(self.model.item_price).label('avg_price')
            )
            .where(self.model.case_id == case_id)
            .group_by(self.model.item_id)
        )
        stats = await self.session.execute(items_stats)

        return {
            'total_openings': total.scalar() or 0,
            'total_value': total_value.scalar() or 0,
            'items_stats': stats.all()
        }

    async def get_opening_by_id(self, opening_id: int, user_id: int) -> Optional[CaseOpeningsOrm]:
        """Получить открытие по ID с проверкой пользователя"""
        query = select(self.model).filter_by(id=opening_id, user_id=user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()