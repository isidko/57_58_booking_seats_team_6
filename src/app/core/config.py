from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.log_level import LogLevel

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    """Settings for all project.

    Firstly, pydantic_settings will look for exported ENV VARS,
    if no env vars exported, it will go to .env file and load from there.
    Settings are case-insensitive => POSTGRES_USER=postgres_user
    https://docs.pydantic.dev/2.2/usage/pydantic_settings/?utm_source=chatgpt.com#dotenv-env-support

    Note. PROJECT_ROOT is used ONLY FOR THE LOCAL STARTUP
    For the docker, we will use ENV VARS everywhere and .env file
    will not be needed.
    """

    app_title: str
    app_description: str

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_dbname: str
    database_echo: bool
    database_command_timeout: int

    first_superuser_email: str
    first_superuser_password: str
    superuser_password_min_length: int

    environment: str
    loglevel: LogLevel

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding='utf-8',
    )

    @field_validator('postgres_port')
    @classmethod
    def validate_port(cls, port: int) -> int:
        """Валидирует номер порта базы данных."""
        if not 1 <= port <= 65535:
            raise ValueError('Номер порта должен быть от 1 до 65535')
        return port


settings = Settings()
