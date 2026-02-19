import secrets
import hmac
import hashlib
from typing import Optional, Set
from fastapi import Request, HTTPException
from fastapi.responses import Response
from fastapi.responses import JSONResponse

from src.config import settings


class CSRFProtection:
    """
    Защита от CSRF атак с использованием Double Submit Cookie pattern
    Токен хранится в cookie и должен быть передан в заголовке X-CSRF-Token
    """

    def __init__(self):
        self.secret_key = settings.CSRF_SECRET_KEY
        self.token_name = "csrf_token"
        self.header_name = "X-CSRF-Token"
        self.token_expiry = 3600  # 1 час

        # Пути, исключенные из CSRF проверки
        self.exempt_paths: Set[str] = {
            "/auth/login",
            "/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

        # Методы, не требующие CSRF проверки
        self.safe_methods: Set[str] = {"GET", "HEAD", "OPTIONS"}

    def _generate_token(self) -> str:
        """Генерирует случайный CSRF токен"""
        return secrets.token_urlsafe(32)

    def _hash_token(self, token: str) -> str:
        """Создает подписанную версию токена"""
        signature = hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{token}.{signature}"

    def _verify_token(self, signed_token: str) -> Optional[str]:
        """Проверяет подпись токена и возвращает оригинальный токен"""
        try:
            token, signature = signed_token.split('.')
            expected = hmac.new(
                self.secret_key.encode(),
                token.encode(),
                hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(signature, expected):
                return token
        except (ValueError, AttributeError):
            pass
        return None

    def set_csrf_token(self, response: Response) -> str:
        """
        Устанавливает CSRF токен в cookie
        Вызывается при GET запросах или после логина
        Возвращает токен для отправки клиенту
        """
        token = self._generate_token()
        signed_token = self._hash_token(token)

        response.set_cookie(
            key=self.token_name,
            value=signed_token,
            httponly=False,  # Должен быть доступен из JavaScript
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",
            max_age=self.token_expiry,
            path="/"
        )

        return token

    def get_csrf_token_from_cookie(self, request: Request) -> Optional[str]:
        """Получает и проверяет CSRF токен из cookie"""
        signed_token = request.cookies.get(self.token_name)
        if not signed_token:
            return None

        return self._verify_token(signed_token)

    def should_validate(self, request: Request) -> bool:
        """Проверяет, нужно ли валидировать CSRF для этого запроса"""
        # Пропускаем безопасные методы
        if request.method in self.safe_methods:
            return False

        # Пропускаем исключенные пути
        if request.url.path in self.exempt_paths:
            return False

        # Пропускаем статические файлы
        if request.url.path.startswith(("/static/", "/assets/")):
            return False

        return True

    def validate_csrf_token(self, request: Request):
        """
        Валидирует CSRF токен для мутирующих запросов (POST, PUT, DELETE)
        Сравнивает токен из cookie с токеном из заголовка
        """
        if not self.should_validate(request):
            return

        # Получаем токен из cookie
        cookie_token = self.get_csrf_token_from_cookie(request)
        if not cookie_token:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "CSRF Error",
                    "message": "CSRF token missing from cookie",
                    "solution": "Please refresh the page and try again"
                }
            )

        # Получаем токен из заголовка
        header_token = request.headers.get(self.header_name)
        if not header_token:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "CSRF Error",
                    "message": f"CSRF token missing from {self.header_name} header",
                    "solution": "Please include X-CSRF-Token header with valid token"
                }
            )

        # Сравниваем токены
        if not hmac.compare_digest(cookie_token, header_token):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "CSRF Error",
                    "message": "CSRF token validation failed",
                    "solution": "Invalid CSRF token. Please refresh the page and try again"
                }
            )

    def clear_csrf_token(self, response: Response):
        """Удаляет CSRF токен при выходе"""
        response.delete_cookie(
            key=self.token_name,
            path="/",
            secure=settings.ENVIRONMENT == "production",
            samesite="lax"
        )

    def add_exempt_path(self, path: str):
        """Добавляет путь в список исключений"""
        self.exempt_paths.add(path)


# Глобальный экземпляр
csrf_protection = CSRFProtection()


# Middleware для CSRF защиты
async def csrf_middleware(request: Request, call_next):
    """Middleware для автоматической проверки CSRF"""

    # Проверяем CSRF только если нужно
    if csrf_protection.should_validate(request):
        try:
            csrf_protection.validate_csrf_token(request)
        except HTTPException as e:
            # Возвращаем красивое сообщение об ошибке

            return JSONResponse(
                status_code=e.status_code,
                content=e.detail if isinstance(e.detail, dict) else {"detail": e.detail}
            )

    response = await call_next(request)
    return response