

from src.api.dependencies import PaginationDep
from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, ItemNotFoundException

from src.schemas.items import Item, ItemAddRequest, ItemAdd, ItemPatchRequest, ItemPatch

from src.services.base import BaseService
from src.services.cases import CaseService



class ItemService(BaseService):
    async def get_item(self, item_id: int, case_id: int):
        return await self.db.items.get_one(case_id=case_id, id=item_id)

    async def get_all_items(
            self,
            case_id: int | None = None,
    ):
        return await self.db.items.get_all(
            case_id=case_id,
        )

    async def create_item(
            self,
            case_id: int,
            item_data: ItemAddRequest,
    ):
        await CaseService(self.db).get_case_with_check(case_id)

        _item_data = ItemAdd(case_id=case_id, **item_data.model_dump())
        item: Item = await self.db.items.add(_item_data)
        await self.db.commit()
        return item

    async def edit_item(
        self,
        case_id: int,
        item_id: int,
        item_data: ItemAddRequest,
    ):
        await CaseService(self.db).get_case_with_check(case_id)
        await self.get_item_with_check(item_id)
        _item_data = ItemAdd(case_id=case_id, **item_data.model_dump())
        await self.db.items.edit(_item_data, id=item_id)
        await self.db.commit()



    async def partially_edit_item(
        self,
        case_id: int,
        item_id: int,
        item_data: ItemPatchRequest,
    ):
        await CaseService(self.db).get_case_with_check(case_id)
        await self.get_item_with_check(item_id)
        _item_data_dict = item_data.model_dump(exclude_unset=True)
        _item_data = ItemPatch(case_id=case_id, **_item_data_dict)
        await self.db.items.edit(_item_data, exclude_unset=True, id=item_id, case_id=case_id)
        await self.db.commit()

    async def delete_item(
            self,
            case_id: int,
            item_id: int,
    ):
        await CaseService(self.db).get_case_with_check(case_id)
        await self.get_item_with_check(item_id)
        await self.db.items.delete(id=item_id, case_id=case_id)
        await self.db.commit()

    async def get_item_with_check(self, item_id: int) -> Item:
        try:
            return await self.db.items.get_one(id=item_id)
        except ObjectNotFoundException:
            raise ItemNotFoundException

    async def get_case_items_with_weights(self, case_id: int):
        """Получает предметы кейса с рассчитанными весами для рандома"""
        items = await self.db.items.get_all(case_id=case_id)

        # Добавляем вес каждому предмету на основе редкости
        for item in items:
            # Вес = редкость^2 * 100 (для более тонкой настройки)
            item.weight = item.rarity ** 2 * 100

        return items












