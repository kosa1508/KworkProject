from fastapi import APIRouter, HTTPException, Query
from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import (
    CaseNotFoundException,
    CaseNotFoundHTTPException,
    ItemNotFoundException,
    ItemNotFoundHTTPException
)
from src.schemas.openings import CaseOpeningRequest, VerifyOpeningRequest
from src.services.openings import CaseOpeningService

router = APIRouter(prefix="/openings", tags=["Открытие кейсов"])


@router.post("/open")
async def open_case(
    user_id: UserIdDep,
    request: CaseOpeningRequest,
    db: DBDep
):
    """
    Открывает кейс для пользователя
    Весь рандом на сервере с криптографическим RNG
    """
    try:
        result = await CaseOpeningService(db).open_case(user_id, request)
        return {"status": "OK", "data": result}
    except InsufficientBalanceException:
        raise InsufficientBalanceHTTPException
    except CaseNotFoundException:
        raise CaseNotFoundHTTPException
    except ItemNotFoundException:
        raise ItemNotFoundHTTPException


@router.get("/history")
async def get_opening_history(
    user_id: UserIdDep,
    db: DBDep,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Получает историю открытий пользователя
    """
    history = await CaseOpeningService(db).get_user_history(user_id, limit)
    return {"status": "OK", "data": history}


@router.post("/verify")
async def verify_opening(
    user_id: UserIdDep,
    request: VerifyOpeningRequest,
    db: DBDep
):
    """
    Проверяет честность открытия кейса
    """
    result = await CaseOpeningService(db).verify_opening(
        user_id=user_id,
        opening_id=request.opening_id,
        server_seed=request.server_seed,
        client_seed=request.client_seed,
        nonce=request.nonce,
        roll=request.roll
    )
    return {"status": "OK", "data": result}