from datetime import date
from fastapi import HTTPException

from sqlalchemy import select


from src.models import PaymentsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import PaymentDataMapper

from src.schemas.payments import PaymentAdd


class PaymentsRepository(BaseRepository):
    model = PaymentsOrm
    mapper = PaymentDataMapper

    async def get_bookings_with_today_checkin(self):
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_payment(self, data: PaymentAdd):
        case = await self.sess.payments.add(data)
        await self.db.commit()
        return case
