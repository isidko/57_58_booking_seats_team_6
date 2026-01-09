"""Модуль `security` инкапсулирует логику аутентификации и авторизации FastAPI-приложения.

Основные возможности:
1. Реализует OAuth2 Password-flow через зависимости `OAuth2PasswordBearer` и `OAuth2PasswordRequestForm`.
2. Генерирует и валидирует JWT-токены (HS256) с полями `sub`, `exp` и `scope`.
3. Поддерживает ролевую модель (`ADMIN`, `MANAGER`, `USER`) и разграничение доступа по скоупам,
   перечисленным в `app.security.constants.Scopes`.
4. Содержит эндпоинт `POST /auth/login`, возвращающий access token.
5. Предоставляет зависимости `get_current_user` и `get_current_active_user` для проверки прав
   в обработчиках маршрутов.

FastAPI docs:
https://fastapi.tiangolo.com/tutorial/security/
https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import (
    ADMIN_PERMISSIONS,
    MANAGER_PERMISSIONS,
    USER_PERMISSIONS,
    Scopes,
)
from app.core.db import get_async_session
from app.models import User as DBUserInstance
from app.models.user import UserRole
from app.schemas.auth import Token, TokenData

router = APIRouter()


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={scope.value: scope.value for scope in Scopes},
)
# он сам вытаскивает header из запроса Authorization Bearerer
#  и возвращает токен


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сверяет введённый пароль с хешем из базы."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля."""
    return password_hash.hash(password)


async def get_user(username: str, session: AsyncSession) -> DBUserInstance | None:
    """Возвращает пользователя по *username* или `None`, если не найден."""
    query = select(DBUserInstance).where(DBUserInstance.username == username)
    return (await session.execute(query)).scalars().first()


async def authenticate_user(login: str, password: str, session: AsyncSession) -> DBUserInstance | bool:
    """Проверяет логин/пароль и возвращает объект пользователя."""
    user: DBUserInstance = await get_user(login, session)
    if not user:
        return False
    # чтобы сравнить пароли, захешируем пришедший и сравним с тем хешем, который есть в БД.
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """Генерирует JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
        required_security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_async_session),
) -> DBUserInstance:
    """Возвращает текущего пользователя.

    required_security_scopes -

     Собирается из всех Security(..., scopes=[...]) в текущей цепочке
     зависимостей для конкретного эндпоинта.

    Сборка required_security_scopes делается во всех защищенных методах через
    Security(callable, scopes=["some_required_scope"])

    В результате, в методе, где мы хотим реально получить эту сборку, передаем
    required_security_scopes: SecurityScopes - это не dependency, просто коллекция
    всех scopes, собранных ранее в дереве зависимостей.

    oauth2_scheme - сам лезет в header, забирает оттуда Bearer и возвращает в token
    Scopes текущего пользователя тащим из токена JWT.
    Далее сравниваем, если есть хотя бы 1 scope из required_security_scopes, которого
    нет в scopes из JWT, отклоняем запрос.
    """
    if required_security_scopes.scopes:
        authenticate_value = f'Bearer scope="{required_security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        # Парсим токен и создаем из него TokenData
        # если токен просрочился или неверный, тут выбросится исключение
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")  # достаем username
        if username is None:
            raise credentials_exception
        scope: str = payload.get("scope", "")  # достаем scope string
        token_scopes = scope.split(" ")  # делим на отрезки
        token_data = TokenData(scopes=token_scopes, username=username)
    # это выбрасывает jwt.decode ИЛИ pydantic из TokenData
    except (InvalidTokenError,ValidationError):
        raise credentials_exception
    # Пытаемся достать пользователя по его username из токена
    user: DBUserInstance = await get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    # Проверяем scopes из токена и необходимые для данного запроса
    for scope in required_security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
        current_user: Annotated[DBUserInstance, Security(get_current_user)],
) -> DBUserInstance:
    """Проверяет, активен ли пользователь."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post(
    "/login",
    summary='Получение токена авторизации',
    description='Возвращает токен для последующей авторизации пользователя.',
)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_async_session),
) -> Token:
    """Эндпоинт для получения JWT по логину/паролю.

    Алгоритм работы:
        1. Проверяем корректность логина и пароля.
        2. Определяем набор scopes в зависимости от роли пользователя.
        3. Генерируем JWT с полями `sub`, `exp` и `scope`.

    OAuth2PasswordRequestForm - создает эндпоинт, принимающий не json, а formdata.
    Он же вытаскивает оттуда все необходимые для аутентификации атрибуты

    Args:
        form_data (OAuth2PasswordRequestForm): Данные формы (логин и пароль)
            для OAuth2 Password-flow.
        session (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        Token: Объект с сгенерированным access token и типом токена.

    """
    user: DBUserInstance = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    if user.role == UserRole.ADMIN:
        scopes = " ".join(ADMIN_PERMISSIONS)
    elif user.role == UserRole.MANAGER:
        scopes = " ".join(MANAGER_PERMISSIONS)
    else:
        scopes = " ".join(USER_PERMISSIONS)
    access_token = create_access_token(
        data={"sub": user.username, "scope": scopes},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
