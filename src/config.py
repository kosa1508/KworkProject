# src/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # Для Alembic - синхронный URL
    @property
    def SYNC_DB_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Для приложения - асинхронный URL
    @property
    def ASYNC_DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Для обратной совместимости (если где-то используется DB_URL)
    @property
    def DB_URL(self) -> str:
        # Возвращаем синхронный URL для Alembic
        return self.SYNC_DB_URL

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    # CSRF настройки
    CSRF_SECRET_KEY: str = "your-csrf-secret-key-change-in-production"
    CSRF_TOKEN_EXPIRY: int = 3600  # 1 час

    # Настройки rate limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 10
    RATE_LIMIT_LOGIN_WINDOW: int = 300  # 5 минут в секундах
    RATE_LIMIT_BLOCK_DURATION: int = 900  # 15 минут блокировки


settings = Settings()