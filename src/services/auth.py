from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import Response

from src.config import settings
from src.exceptions import IncorrectTokenException, EmailNotRegisteredException, IncorrectPasswordException, \
    ObjectAlreadyExistsException, UserAlreadyExistsException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.base import BaseService

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 60


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise IncorrectTokenException

    async def register_user(self, data: UserRequestAdd):
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException as ex:
            raise UserAlreadyExistsException from ex

    async def login_user(self, data: UserRequestAdd, response: Response) -> str:
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise EmailNotRegisteredException
        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException

        access_token = self.create_access_token({"user_id": user.id})

        # Устанавливаем cookie с защитными флагами
        self._set_auth_cookie(response, access_token)

        return access_token

    def _set_auth_cookie(self, response: Response, token: str):
        """Установка защищенной cookie с JWT токеном"""
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,  # Защита от XSS - недоступно из JavaScript
            secure=settings.ENVIRONMENT == "production",  # Только по HTTPS в продакшене
            samesite="lax",  # Защита от CSRF
            max_age=ACCESS_TOKEN_EXPIRE_SECONDS,  # Время жизни cookie
            expires=ACCESS_TOKEN_EXPIRE_SECONDS,  # Для совместимости
            path="/",  # Доступна для всех путей
            domain=None  # Ограничиваем текущим доменом
        )

    def logout_user(self, response: Response):
        """Удаление cookie при выходе"""
        response.delete_cookie(
            key="access_token",
            path="/",
            domain=None,
            secure=settings.ENVIRONMENT == "production",
            httponly=True,
            samesite="lax"
        )

    async def get_one_or_none_user(self, user_id: int):
        return await self.db.users.get_one_or_none(id=user_id)