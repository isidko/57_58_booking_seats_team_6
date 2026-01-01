from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy 2.0."""

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Автоматическое именование таблиц.

        Проверяем, не переопределен ли вручную
        """
        if hasattr(cls, '_custom_tablename'):
            return cls._custom_tablename
        return f'{cls.__name__.lower()}s'


# Создаем движок
engine = create_async_engine(
    url=f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_dbname}",
    pool_pre_ping=True,
    echo=settings.database_echo,
    connect_args={
        "command_timeout": settings.database_command_timeout,
        "server_settings": {
            "application_name": settings.app_title,
            "timezone": "UTC",
        },
    },
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения асинхронной сессии."""
    async with AsyncSessionLocal() as async_session:
        try:
            yield async_session
        except SQLAlchemyError:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
