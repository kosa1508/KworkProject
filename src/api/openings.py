from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import List, Optional

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import (
    CaseNotFoundException,
    CaseNotFoundHTTPException,
    ItemNotFoundException,
    ItemNotFoundHTTPException,
    UserNotFoundException,
    UserNotFoundHTTPException,
    InsufficientBalanceException,
    InsufficientBalanceHTTPException,
)
from src.schemas.openings import (
    OpeningRequest,
    OpeningResponse,
    OpeningVerifyRequest,
    OpeningVerifyResponse,
    OpeningHistoryItem,
    CaseContents
)
from src.services.openings import CaseOpeningService
from src.services.cases import CaseService
from src.core.rate_limit import rate_limit
from src.core.csrf import csrf_protect

router = APIRouter(prefix="/openings", tags=["Открытие кейсов"])


@router.get("/case/{case_id}/contents", response_model=CaseContents)
async def get_case_contents(
        case_id: int,
        db: DBDep
):
    """
    Получить содержимое кейса с шансами выпадения
    """
    try:
        contents = await CaseService(db).get_case_contents(case_id)
        return contents
    except CaseNotFoundException:
        raise CaseNotFoundHTTPException


@router.post("/open", response_model=OpeningResponse)
@rate_limit(max_calls=10, period=3600)  # 10 открытий в час
@csrf_protect
async def open_case(
        request: Request,
        user_id: UserIdDep,
        opening_request: OpeningRequest,
        db: DBDep,
        user_agent: Optional[str] = Header(None)
):
    """
    Открыть кейс
    """
    try:
        # Получаем IP клиента
        client_ip = request.client.host if request.client else None

        result = await CaseOpeningService(db).open_case(
            user_id=user_id,
            request=opening_request,
            client_ip=client_ip,
            user_agent=user_agent
        )
        return result

    except CaseNotFoundException:
        raise CaseNotFoundHTTPException
    except ItemNotFoundException:
        raise ItemNotFoundHTTPException
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except InsufficientBalanceException:
        raise InsufficientBalanceHTTPException
        # Это нормально, просто возвращаем существующий результат
        pass


@router.get("/history", response_model=List[OpeningHistoryItem])
async def get_opening_history(
        user_id: UserIdDep,
        db: DBDep,
        limit: int = 20,
        offset: int = 0
):
    """
    Получить историю открытий пользователя
    """
    history = await CaseOpeningService(db).get_user_history(user_id, limit, offset)
    return history


@router.post("/verify", response_model=OpeningVerifyResponse)
async def verify_opening(
        user_id: UserIdDep,
        request: OpeningVerifyRequest,
        db: DBDep
):
    """
    Проверить честность открытия
    """
    result = await CaseOpeningService(db).verify_opening(user_id, request)
    return result


@router.get("/stats/{case_id}")
async def get_case_stats(
        case_id: int,
        db: DBDep
):
    """
    Получить статистику открытий кейса
    """
    try:
        stats = await CaseOpeningService(db).get_opening_stats(case_id)
        return stats
    except CaseNotFoundException:
        raise CaseNotFoundHTTPException