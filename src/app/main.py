from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.routers import main_router
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.log_level import LogLevel
from app.core.logging import configure_logging, log_message
from app.exceptions.common import AppError
from app.models import User, UserRole

configure_logging()

password_hash = PasswordHash.recommended()


async def ensure_superuser() -> None:
    """Создает суперпользователя при старте приложения, если он не существует."""
    log_message(
        "Проверка наличия суперпользователя...",
        level=LogLevel.INFO,
    )

    if not (settings.first_superuser_email and settings.first_superuser_password):
        log_message(
            "Настройки суперпользователя не заданы. "
            "Пропускаем создание суперпользователя.",
            level=LogLevel.WARNING,
        )
        return

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(User).where(User.email == settings.first_superuser_email),
        )
        user = res.scalar_one_or_none()
        if user:
            log_message(
                f"Суперпользователь уже существует: {settings.first_superuser_email}",
                level=LogLevel.INFO,
            )
            return

        username = getattr(settings, "SUPERUSER_USERNAME", "admin")
        log_message(
            f"Создание суперпользователя: email={settings.first_superuser_email}, "
            f"username={username}",
            level=LogLevel.INFO,
        )

        user = User(
            email=settings.first_superuser_email,
            username=username,
            password_hash=password_hash.hash(settings.first_superuser_password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)

        try:
            await session.commit()
            log_message(
                f"Суперпользователь успешно создан: {settings.first_superuser_email}",
                level=LogLevel.INFO,
            )
        except IntegrityError:
            await session.rollback()
            log_message(
                f"Попытка создания суперпользователя {settings.first_superuser_email} "
                "не удалась из-за нарушения уникальности. "
                "Возможно, он был создан.",
                level=LogLevel.WARNING,
            )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управляет жизненным циклом приложения.

    При старте создает суперпользователя, если он не существует.
    """
    await ensure_superuser()
    yield


app = FastAPI(title=settings.app_title, lifespan=lifespan)

app.include_router(main_router)


@app.exception_handler(AppError)  # noqa: F821
async def app_error_handler(
        request: Request,
        exc: AppError,
) -> JSONResponse:
    """Обработчик исключений приложения.

    https://fastapi.tiangolo.com/ru/tutorial/handling-errors/

    Args:
        request: HTTP запрос.
        exc: Исключение приложения.

    Returns:
        JSONResponse

    """
    logger.opt(exception=exc).bind(user_id=None, username="SYSTEM").error(
        "{method} {url}\n{type}: {code} - {msg}",
        method=request.method,
        url=request.url,
        type=exc.__class__.__name__,
        code=exc.status_code,
        msg=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.__class__.__name__},
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        log_level=None,
        access_log=False,
    )
