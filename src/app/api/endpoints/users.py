"""API endpoints для User.

Задачи слоя endpoints:
- Принять HTTP-запрос (параметры path/query/body).
- Выполнить проверку JWT/scopes через Security(get_current_user, scopes=[...]).
- Проверить права доступа на основе роли пользователя.
- Вызвать CRUD слой с уже готовыми параметрами.
"""

from typing import Any

from fastapi import APIRouter, Depends, Path, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_active_user, get_password_hash
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.crud.user import user_crud
from app.exceptions.api import ForbiddenError
from app.exceptions.database import DBConflictError, DBObjectNotFoundError
from app.models import User
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserInfo, UserUpdate

router = APIRouter()


@router.get(
    '/',
    response_model=list[UserInfo],
    summary='Получение списка пользователей',
    description=(
        'Возвращает информацию о всех пользователях. Только для '
        'администраторов или менеджеров'
    ),
)
async def list_users(
    *,
    session: AsyncSession = Depends(get_async_session),
    _: User = Security(get_current_active_user, scopes=[Scopes.USERS_READ]),
) -> Any:
    """Получить список пользователей.

    Доступ:
    - ADMIN, MANAGER: могут видеть всех пользователей.
    - USER: доступ запрещён (не имеет scope USERS_READ).
    """
    return await user_crud.get_multi(
        session=session,
        active_objects_only=False,
    )


@router.post(
    '/',
    response_model=UserInfo,
    summary='Регистрация нового пользователя',
    description=(
        'Создает нового пользователя с указанными данными.\n\n'
        'Обязательные поля:\n'
        '- username\n'
        '- password\n'
        '- email или phone'
    ),
)
async def create_user(
    *,
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserInfo:
    """Создать нового пользователя.

    Обязательные поля:
    - username: имя пользователя (должно быть уникальным)
    - password: пароль
    - email или phone: хотя бы одно из этих полей должно быть указано

    Доступ:
    - Доступно всем (не требуется авторизация).

    Валидация:
    - Проверяет уникальность username, email и phone.
    """
    # Проверяем уникальность
    existing_user = await user_crud.get_by_username(session, user_in.username)
    if existing_user:
        raise DBConflictError(message=f'Пользователь с username "{user_in.username}" уже существует')

    password_hash = get_password_hash(user_in.password)

    # Создаём пользователя через CRUD (там проверяется email и phone)
    try:
        db_user = await user_crud.create(
            session=session,
            obj_in=user_in,
            password_hash=password_hash,
        )
    except ValueError as e:
        raise DBConflictError(message=str(e))

    return UserInfo.model_validate(db_user)


@router.get(
    '/me',
    response_model=UserInfo,
    summary='Получение информации о текущем пользователе',
    description=(
        'Возвращает информацию о текущем пользователе. Только для '
        'авторизированных пользователей'
    ),
)
async def get_current_user_info(
    *,
    current_user: User = Security(get_current_active_user, scopes=[Scopes.USERS_ME]),
) -> UserInfo:
    """Получить информацию о текущем пользователе.

    Доступ:
    - Все авторизованные пользователи могут получить информацию о себе.
    """
    return UserInfo.model_validate(current_user)


@router.patch(
    '/me',
    response_model=UserInfo,
    summary='Обновление информации о текущем пользователе',
    description=(
        'Возвращает обновленную информацию о пользователе. Только для '
        'авторизированных пользователей'
    ),
)
async def update_current_user(
    *,
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(get_current_active_user, scopes=[Scopes.USERS_UPDATE]),
) -> UserInfo:
    """Обновить информацию о текущем пользователе.

    Доступ:
    - Все авторизованные пользователи могут обновлять свою информацию.
    - Пользователь не может изменять роль и статус активности.

    Валидация:
    - Проверяет уникальность username, email и phone (если они изменяются).
    """
    # Пользователь не может изменять роль и is_active
    if user_in.role is not None:
        raise ForbiddenError('User cannot change their role')
    if user_in.is_active is not None:
        raise ForbiddenError('User cannot change their active status')

    # Если передан пароль, нужно его захешировать
    update_data = user_in.model_dump(exclude_unset=True)
    has_password = 'password' in update_data

    if has_password:
        current_user.password_hash = get_password_hash(update_data.pop('password'))
        # Обновляем остальные поля
        for key, value in update_data.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
        # Сохраняем изменения
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
        db_user = current_user
    else:
        # Обновляем через CRUD (без пароля) - там проверяется уникальность email/phone
        db_user = await user_crud.update(
            session=session,
            db_obj=current_user,
            obj_in=user_in,
        )

    return UserInfo.model_validate(db_user)


@router.get(
    '/{user_id}',
    response_model=UserInfo,
    summary='Получение информации о пользователе по его ID',
    description=(
        'Возвращает информацию о пользователе по его ID. Только для '
        'администраторов или менеджеров'
    ),
)
async def get_user(
    *,
    user_id: int = Path(..., title='User ID', examples=[1]),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(get_current_active_user, scopes=[Scopes.USERS_READ]),
) -> UserInfo:
    """Получить пользователя по ID.

    Доступ:
    - USER: может получить только свою информацию.
    - ADMIN, MANAGER: могут получить информацию о любом пользователе.
    """
    if current_user.role == UserRole.USER:
        if user_id != current_user.id:
            raise ForbiddenError('USER can only view their own information')
        return UserInfo.model_validate(current_user)

    user = await user_crud.get_by_pk(session=session, pk=user_id)
    if not user:
        raise DBObjectNotFoundError(message=f'User with ID {user_id} not found')

    return UserInfo.model_validate(user)


@router.patch(
    '/{user_id}',
    response_model=UserInfo,
    summary='Обновление информации о пользователе по его ID',
    description=(
        'Возвращает обновленную информацию о пользователе по его ID. Только '
        'для администраторов или менеджеров'
    ),
)
async def update_user(
    *,
    user_id: int = Path(..., title='User ID', examples=[1]),
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(get_current_active_user, scopes=[Scopes.USERS_UPDATE]),
) -> UserInfo:
    """Обновить информацию о пользователе.

    Доступ:
    - USER: может обновлять только свою информацию.
        - Не может изменять роль и is_active.
    - ADMIN, MANAGER: могут обновлять любых пользователей.
    """
    # Получаем пользователя для обновления
    if current_user.role == UserRole.USER:
        if user_id != current_user.id:
            raise ForbiddenError('USER can only update their own information')

        # USER не может изменять роль и is_active
        if user_in.role is not None:
            raise ForbiddenError('USER cannot change their role')
        if user_in.is_active is not None:
            raise ForbiddenError('USER cannot change their active status')

        existing_user = current_user
    else:
        existing_user = await user_crud.get_by_pk(session=session, pk=user_id)
        if not existing_user:
            raise DBObjectNotFoundError(message=f'User with ID {user_id} not found')

        # MANAGER не может изменять роль (только ADMIN)
        if current_user.role == UserRole.MANAGER and user_in.role is not None:
            raise ForbiddenError('MANAGER cannot change user role')

    # Если передан пароль, нужно его захешировать
    update_data = user_in.model_dump(exclude_unset=True)
    has_password = 'password' in update_data

    if has_password:
        existing_user.password_hash = get_password_hash(update_data.pop('password'))
        # Обновляем остальные поля
        for key, value in update_data.items():
            if hasattr(existing_user, key):
                setattr(existing_user, key, value)
        # Сохраняем изменения
        session.add(existing_user)
        await session.commit()
        await session.refresh(existing_user)
        db_user = existing_user
    else:
        db_user = await user_crud.update(
            session=session,
            db_obj=existing_user,
            obj_in=user_in,
        )

    return UserInfo.model_validate(db_user)
