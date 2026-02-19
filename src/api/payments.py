from fastapi import APIRouter

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.payments import PaymentAddRequest
from src.services.payments import PaymentService

router = APIRouter(prefix="/payments", tags=["Платежи"])

@router.get("")
async def get_payments(db: DBDep):
    return await PaymentService(db).get_payments()


@router.get("/me")
async def get_my_payments(
    db: DBDep,
    user_id: UserIdDep,
):
    return await PaymentService(db).get_my_payments(user_id)


@router.post("")
async def add_payment(
    user_id: UserIdDep,
    db: DBDep,
    payment_data: PaymentAddRequest,
):
    payment = await PaymentService(db).add_payment(user_id, payment_data)
    return {"status": "OK", "data": payment}













