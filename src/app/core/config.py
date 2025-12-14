from typing import Optional

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    app_title: str = 'Бронирование мест в кафе'

    secret: str = 'SECRET'

    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    postgres_user: str
    postgres_password: str
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str

    pool_size: int = 20
    max_overflow: int = 10
    pool_recycle: int = 3600

    database_pool_pre_ping: bool = True
    database_echo: bool = False  # Логирование SQL (True для разработки)

    @property
    def sync_database_url(self) -> str:
        """Формирует синхронный URL для подключения к PostgreSQL.

        Используется для Alembic миграций и синхронных операций с БД.
        Использует драйвер psycopg2.
        """
        return (
            f'postgresql://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )

    @property
    def async_database_url(self) -> str:
        """Формирует асинхронный URL для подключения к PostgreSQL.

        Используется для основного приложения на FastAPI.
        Использует драйвер asyncpg.
        """
        return (
            'postgresql+asyncpg://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )

    @property
    def docker_database_url(self) -> str:
        """Формирует URL для подключения внутри Docker Compose сети."""
        if self.postgres_host != 'localhost':
            host = self.postgres_host
        else:
            host = 'postgres'
        return (
            'postgresql+asyncpg://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{host}:{self.postgres_port}/{self.postgres_db}'
        )

    @field_validator('postgres_port')
    @classmethod
    def validate_port(cls, port: int) -> int:
        """Валидирует номер порта базы данных."""
        if not 1 <= port <= 65535:
            raise ValueError('Номер порта должен быть от 1 до 65535')
        return port

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
        env_prefix='',
    )


settings = Settings()
