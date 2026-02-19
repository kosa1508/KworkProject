from datetime import date

from src.api.dependencies import PaginationDep
from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException
from src.schemas.cases import CaseAdd, CasePatch, Case
from src.services.base import BaseService


class CaseService(BaseService):

    async def get_all_cases(
            self,
    ):
        return await self.db.cases.get_all()

    async def get_filtered_by_time(
            self,
            pagination,
            location: str | None,
            title: str | None,
            date_from: date,
            date_to: date,
    ):
        check_date_to_after_date_from(date_from, date_to)
        per_page = pagination.per_page or 5
        return await self.db.cases.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_case(self, case_id: int):
        return await self.db.cases.get_one(id=case_id)

    async def add_case(self, data: CaseAdd):
        case = await self.db.cases.add(data)
        await self.db.commit()
        return case

    async def edit_case(self, case_id: int, data: CaseAdd):
        await self.db.cases.edit(data, id=case_id)
        await self.db.commit()

    async def edit_case_partially(self, case_id: int, data: CasePatch, exclude_unset: bool = False):
        await self.db.cases.edit(data, exclude_unset=exclude_unset, id=case_id)
        await self.db.commit()

    async def delete_case(self, case_id: int):
        await self.db.cases.delete(id=case_id)
        await self.db.commit()

    async def get_case_with_check(self, case_id: int) -> Case:
        try:
            return await self.db.cases.get_one(id=case_id)
        except ObjectNotFoundException:
            raise CaseNotFoundException
