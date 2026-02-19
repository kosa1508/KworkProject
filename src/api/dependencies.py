from typing import Annotated, Optional

from fastapi import Query, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.database import async_session_maker
from src.exceptions import IncorrectTokenException, IncorrectTokenHTTPException, NoAccessTokenHTTPException
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(5, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]

# Для работы с Authorization header
security = HTTPBearer(auto_error=False)


def get_token_from_cookie(request: Request) -> Optional[str]:
    """Извлекает токен из cookie"""
    return request.cookies.get("access_token", None)


def get_token_from_header(credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)] = None) -> \
Optional[str]:
    """Извлекает токен из Authorization header"""
    if credentials:
        return credentials.credentials
    return None


def get_token_optional(
        token_from_cookie: Optional[str] = Depends(get_token_from_cookie),
        token_from_header: Optional[str] = Depends(get_token_from_header),
) -> Optional[str]:
    """
    Получает токен из cookie или header (опционально)
    Возвращает None если токена нет
    """
    return token_from_cookie or token_from_header


def get_token_required(
        token_from_cookie: Optional[str] = Depends(get_token_from_cookie),
        token_from_header: Optional[str] = Depends(get_token_from_header),
) -> str:
    """
    Получает токен из cookie или header (обязательно)
    Если токена нет - выбрасывает исключение
    """
    token = token_from_cookie or token_from_header
    if not token:
        raise NoAccessTokenHTTPException
    return token


def get_current_user_id(
        token: str = Depends(get_token_required),
) -> int:
    """
    Получает ID текущего пользователя из токена
    """
    try:
        data = AuthService().decode_token(token)
        user_id = data.get("user_id")
        if not user_id:
            raise IncorrectTokenException
    except IncorrectTokenException:
        raise IncorrectTokenHTTPException
    return user_id


# Для эндпоинтов, где пользователь может быть не авторизован
def get_current_user_id_optional(
        token: Optional[str] = Depends(get_token_optional),
) -> Optional[int]:
    """
    Получает ID текущего пользователя из токена (опционально)
    Возвращает None если пользователь не авторизован
    """
    if not token:
        return None

    try:
        data = AuthService().decode_token(token)
        return data.get("user_id")
    except IncorrectTokenException:
        return None


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


# Типы для аннотаций
UserIdDep = Annotated[int, Depends(get_current_user_id)]
OptionalUserIdDep = Annotated[Optional[int], Depends(get_current_user_id_optional)]
DBDep = Annotated[DBManager, Depends(get_db)]
TokenDep = Annotated[str, Depends(get_token_required)]
OptionalTokenDep = Annotated[Optional[str], Depends(get_token_optional)]