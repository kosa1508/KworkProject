# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool

from src.config import settings

# Используем асинхронный URL для движков приложения
db_params = {}

engine = create_async_engine(settings.ASYNC_DB_URL, echo=True, **db_params)

engine_null_pool = create_async_engine(settings.ASYNC_DB_URL, echo=True, poolclass=NullPool)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)

class Base(DeclarativeBase):
    pass