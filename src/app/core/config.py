import os
from pathlib import Path

from fastapi_mail import ConnectionConfig
from pydantic import SecretStr, field_validator
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
    postgres_db: str
    database_echo: bool
    database_command_timeout: int

    first_superuser_email: str
    first_superuser_password: str
    superuser_password_min_length: int

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Mail settings
    mail_username: str | None = None
    mail_password: SecretStr | None = None
    mail_from: str | None = None
    mail_port: int = 1025
    mail_server: str = "localhost"
    mail_starttls: bool = False
    mail_ssl_tls: bool = False
    use_credentials: bool = False

    # Celery / Broker settings
    rabbitmq_default_user: str
    rabbitmq_default_pass: str
    rabbitmq_host: str
    rabbitmq_port: int
    celery_result_backend: str
    celery_timezone: str

    environment: str | None = 'LOCAL'
    loglevel: LogLevel

    # если ENVIRONMENT env var отсутствует, используем .env.local
    # в остальных случаях - .env
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env.local" if not os.getenv(
            'ENVIRONMENT', None) else PROJECT_ROOT / ".env",
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

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
)
