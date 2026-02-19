from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import JSONResponse

from src.api.dependencies import DBDep, get_current_user_id
from src.config import settings
from src.exceptions import IncorrectPasswordHTTPException, IncorrectPasswordException, \
    EmailNotRegisteredHTTPException, EmailNotRegisteredException, UserAlreadyExistsException, \
    UserEmailAlreadyExistsHTTPException
from src.schemas.users import UserRequestAdd
from src.services.auth import AuthService
from src.core.rate_limiter import rate_limiter
from src.core.csrf import csrf_protection

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
        data: UserRequestAdd,
        response: Response,
        request: Request,
        db: DBDep,
):
    # Получаем IP для rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # Проверяем rate limit перед обработкой запроса (для регистрации)
    is_allowed, retry_after = await rate_limiter.is_allowed(client_ip, data.email, action="register")

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many registration attempts",
                "message": f"Слишком много попыток регистрации. Попробуйте снова через {retry_after} секунд.",
                "retry_after": retry_after
            }
        )

    try:
        await AuthService(db).register_user(data)

        # Сбрасываем счетчик попыток при успешной регистрации
        await rate_limiter.reset_attempts(client_ip, data.email, action="register")

        # Устанавливаем CSRF токен после успешной регистрации
        csrf_token = csrf_protection.set_csrf_token(response)

        return JSONResponse(
            content={
                "status": "OK",
                "csrf_token": csrf_token
            },
            headers={"X-CSRF-Token": csrf_token}
        )
    except UserAlreadyExistsException:
        # Увеличиваем счетчик неудачных попыток (email уже существует)
        await rate_limiter.add_attempt(client_ip, data.email, action="register")
        raise UserEmailAlreadyExistsHTTPException


@router.post("/login")
async def login_user(
        data: UserRequestAdd,
        response: Response,
        request: Request,
        db: DBDep,
):
    # Получаем IP для rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # Проверяем rate limit перед обработкой запроса
    is_allowed, retry_after = await rate_limiter.is_allowed(client_ip, data.email, action="login")

    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many login attempts",
                "message": f"Слишком много попыток входа. Попробуйте снова через {retry_after} секунд.",
                "retry_after": retry_after
            }
        )

    try:
        auth_service = AuthService(db)
        access_token = await auth_service.login_user(data, response)

        # Сбрасываем счетчик попыток при успешном входе
        await rate_limiter.reset_attempts(client_ip, data.email, action="login")

        # Устанавливаем CSRF токен после успешного входа
        csrf_token = csrf_protection.set_csrf_token(response)

        return JSONResponse(
            content={
                "access_token": access_token,
                "csrf_token": csrf_token
            },
            headers={"X-CSRF-Token": csrf_token}
        )

    except EmailNotRegisteredException:
        # Увеличиваем счетчик неудачных попыток
        await rate_limiter.add_attempt(client_ip, data.email, action="login")
        raise EmailNotRegisteredHTTPException

    except IncorrectPasswordException:
        # Увеличиваем счетчик неудачных попыток
        await rate_limiter.add_attempt(client_ip, data.email, action="login")
        raise IncorrectPasswordHTTPException


@router.get("/me")
async def get_me(
        request: Request,
        db: DBDep,
        user_id: int = Depends(get_current_user_id),
):
    user = await AuthService(db).get_one_or_none_user(user_id)

    # Для GET запросов CSRF не проверяется, но обновляем токен
    response = JSONResponse(content=user)

    # Обновляем CSRF токен если пользователь авторизован
    if user_id:
        csrf_protection.set_csrf_token(response)

    return response


@router.post("/logout")
async def logout(
        response: Response,
        db: DBDep,
        request: Request,
):
    # Удаляем CSRF токен
    csrf_protection.clear_csrf_token(response)

    # Выходим из системы
    AuthService(db).logout_user(response)

    return {"status": "OK"}


# Добавим эндпоинт для получения статуса rate limit для регистрации
@router.get("/register-attempts/{email}")
async def get_register_attempts(
        email: str,
        request: Request,
):
    """Получить количество попыток регистрации для email (только для отладки)"""
    client_ip = request.client.host if request.client else "unknown"
    attempts = await rate_limiter.get_attempts(client_ip, email, action="register")
    return {"attempts": attempts}


# Добавим эндпоинт для получения статуса rate limit для логина
@router.get("/login-attempts/{email}")
async def get_login_attempts(
        email: str,
        request: Request,
):
    """Получить количество попыток входа для email (только для отладки)"""
    client_ip = request.client.host if request.client else "unknown"
    attempts = await rate_limiter.get_attempts(client_ip, email, action="login")
    return {"attempts": attempts}


@router.post("/test-rate-limit")
async def test_rate_limit(request: Request):
    """Тестовый эндпоинт для демонстрации rate limiting"""
    client_ip = request.client.host if request.client else "unknown"
    test_email = "test@example.com"

    results = []

    # Симулируем 12 попыток входа
    for i in range(12):
        is_allowed, retry_after = await rate_limiter.is_allowed(client_ip, test_email, action="login")

        if is_allowed:
            # Имитируем неудачную попытку
            is_allowed, retry_after = await rate_limiter.add_attempt(client_ip, test_email, action="login")
            results.append({
                "attempt": i + 1,
                "status": "failed",
                "blocked": not is_allowed,
                "retry_after": retry_after
            })
        else:
            results.append({
                "attempt": i + 1,
                "status": "blocked",
                "retry_after": retry_after
            })
            break

    # Получаем финальное состояние
    attempts = await rate_limiter.get_attempts(client_ip, test_email, action="login")

    return {
        "results": results,
        "final_attempts": attempts,
        "client_ip": client_ip,
        "message": f"После {settings.RATE_LIMIT_LOGIN_ATTEMPTS} неудачных попыток доступ заблокирован на {settings.RATE_LIMIT_BLOCK_DURATION} секунд"
    }


# Пример защищенного эндпоинта для демонстрации
@router.post("/protected-action")
async def protected_action(
        request: Request,
        user_id: int = Depends(get_current_user_id),
):
    """
    Пример эндпоинта, защищенного от CSRF
    Требует наличие X-CSRF-Token в заголовках
    """
    # CSRF проверяется автоматически middleware
    return {
        "message": "Action completed successfully",
        "user_id": user_id,
        "csrf_protected": True
    }