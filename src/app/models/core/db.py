import os
from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.pool import QueuePool


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy 2.0."""

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Автоматическое именование таблиц."""
        return f"{cls.__name__.lower()}s"


def get_database_url() -> str:
    """Выбирает правильный URL в зависимости от окружения."""
    if os.getenv('DOCKER_MODE', 'false').lower() == 'true':
        return settings.docker_database_url
    return settings.async_database_url


# Создаем движок
engine: AsyncEngine = create_async_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_recycle=settings.pool_recycle,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=settings.database_pool_pre_ping,
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
        except Exception:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
