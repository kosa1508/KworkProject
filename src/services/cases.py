from datetime import date
from typing import List, Optional

from src.api.dependencies import PaginationDep
from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, CaseNotFoundException
from src.schemas.cases import CaseCreate, CaseUpdate, Case, CaseWithStats
from src.services.base import BaseService
from src.services.rng import CryptoRNGService


class CaseService(BaseService):

    async def get_all_cases(self, only_active: bool = True) -> List[Case]:
        """Получение всех кейсов"""
        filters = {}
        if only_active:
            filters['is_active'] = True

        return await self.db.cases.get_all(
            order_by='sort_order',
            **filters
        )

    async def get_case(self, case_id: int) -> Case:
        """Получение конкретного кейса"""
        try:
            return await self.db.cases.get_one(id=case_id)
        except ObjectNotFoundException:
            raise CaseNotFoundException

    async def get_case_with_stats(self, case_id: int) -> CaseWithStats:
        """Получение кейса со статистикой"""
        case = await self.get_case(case_id)

        # Получаем статистику открытий
        stats = await self.db.openings.get_case_stats(case_id)

        # Получаем количество предметов в кейсе
        items = await self.db.items.get_all(case_id=case_id, is_active=True)

        case_dict = case.model_dump()
        case_dict.update({
            'total_openings': stats['total_openings'],
            'total_value': stats['total_value'],
            'items_count': len(items)
        })

        return CaseWithStats(**case_dict)

    async def get_case_contents(self, case_id: int) -> dict:
        """Получение содержимого кейса с шансами"""
        case = await self.get_case(case_id)
        items = await self.db.items.get_all(case_id=case_id, is_active=True)

        # Конвертируем в словари для расчета
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

        # Рассчитываем шансы
        items_with_chances = CryptoRNGService.calculate_item_chances(items_dicts)

        return {
            'case_id': case.id,
            'case_name': case.name,
            'items': items_with_chances,
            'total_value': sum(item['base_price'] for item in items),
            'avg_price': sum(item['base_price'] for item in items) / len(items) if items else 0
        }

    async def create_case(self, data: CaseCreate) -> Case:
        """Создание нового кейса"""
        case = await self.db.cases.add(data.model_dump())
        await self.db.commit()
        return case

    async def update_case(self, case_id: int, data: CaseUpdate) -> Case:
        """Обновление кейса"""
        await self.get_case(case_id)

        update_data = data.model_dump(exclude_unset=True)
        await self.db.cases.edit(update_data, id=case_id)
        await self.db.commit()

        return await self.get_case(case_id)

    async def delete_case(self, case_id: int):
        """Удаление кейса (мягкое удаление через is_active)"""
        await self.update_case(case_id, CaseUpdate(is_active=False))