from sqlalchemy import select, and_
from src.models import CaseOpeningsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CaseOpeningDataMapper


class CaseOpeningsRepository(BaseRepository):
    model = CaseOpeningsOrm
    mapper = CaseOpeningDataMapper

    async def get_user_openings(self, user_id: int, limit: int = 50):
        query = (
            select(self.model)
            .filter_by(user_id=user_id)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_schema_entity(model) for model in result.scalars().all()]

    async def get_opening_by_id(self, opening_id: int, user_id: int):
        query = select(self.model).filter_by(id=opening_id, user_id=user_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.mapper.map_to_schema_entity(model) if model else None