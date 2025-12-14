import contextlib

from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import get_user_db, get_user_manager
from app.schemas.user import UserCreate
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
    email: EmailStr,
    password: str,
    is_superuser: bool = False,
    is_active: bool = True,
    is_verified: bool = False,
) -> bool:
    """Создает нового пользователя в системе."""
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser,
                            is_active=is_active,
                            is_verified=is_verified,
                        ),
                    )
                    return True
    except UserAlreadyExists:
        return False


async def create_first_superuser() -> bool:
    """Создает первого суперпользователя при запуске приложения."""
    if (
        not settings.first_superuser_email or
        not settings.first_superuser_password
    ):
        return False

    return await create_user(
        email=settings.first_superuser_email,
        password=settings.first_superuser_password,
        is_superuser=True,
        is_active=True,
        is_verified=True,
    )
