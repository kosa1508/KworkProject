from src.exceptions import ObjectNotFoundException, CaseNotFoundException
from src.schemas.cases import Case
from src.schemas.payments import PaymentAddRequest, PaymentAdd
from src.services.base import BaseService


class PaymentService(BaseService):
    async def add_payment(self, user_id: int, payment_data: PaymentAddRequest):
        try:
            case: Case = await self.db.cases.get_one(id=payment_data.case_id)
        except ObjectNotFoundException as ex:
            raise CaseNotFoundException from ex
        case_price: int = case.price
        _payment_data = PaymentAdd(
            user_id=user_id,
            price=case_price,
            **payment_data.dict(),
        )
        payment = await self.db.payments.add(_payment_data)
        await self.db.commit()
        return payment

    async def get_payments(self):
        return await self.db.payments.get_all()

    async def get_my_payments(self, user_id: int):
        return await self.db.payments.get_filtered(user_id=user_id)
