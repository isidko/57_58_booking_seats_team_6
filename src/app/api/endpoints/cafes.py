"""API endpoints для Cafe.

Задачи слоя endpoints:
- Принять HTTP-запрос (параметры path/query/body).
- Выполнить проверку JWT/scopes через Security(get_current_user, scopes=[...]).
- Делегировать проверку правил и построение фильтра в CafePolicy.
- Вызвать CRUD слой с уже готовыми параметрами.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.crud.cafe import CRUDCafe
from app.models.user import User, UserRole
from app.policies.cafe import CafePolicy
from app.schemas.cafe import CafeCreate, CafeInfo, CafeUpdate

router = APIRouter()
crud_cafe = CRUDCafe()
policy = CafePolicy()

CurrentUserRead = Annotated[
    User,
    Security(get_current_user, scopes=[Scopes.CAFES_READ.value]),
]


async def _validate_managers_ids(
    session: AsyncSession,
    managers_id: list[int],
) -> list[int]:
    """Проверяет список managers_id."""
    unique_ids = list(dict.fromkeys(managers_id))

    res = await session.execute(
        select(User.id).where(User.id.in_(unique_ids), User.role == UserRole.MANAGER),
    )
    ok_ids = {row[0] for row in res.all()}

    if ok_ids != set(unique_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid managers_id: not found or not MANAGER',
        )

    return unique_ids


@router.get('', response_model=list[CafeInfo])
async def get_list_cafes(
    current_user: CurrentUserRead,
    show_all: bool = False,
    session: AsyncSession = Depends(get_async_session),
) -> list[CafeInfo]:
    """Получить список кафе.

    Параметры:
    - show_all=False: по умолчанию возвращаются только активные
     (и дополнительно действует фильтр по роли согласно policy).
    - show_all=True: разрешён не всем ролям (ограничения описаны в policy).

    Возвращает:
    - список CafeInfo.
    """
    ctx = policy.read_context(current_user=current_user, show_all=show_all)
    return await crud_cafe.get_multi(
        session,
        active_objects_only=ctx.active_objects_only,
        where_expr=ctx.where_expr,
    )


@router.get('/{cafe_id}', response_model=CafeInfo)
async def get_cafe(
    cafe_id: int,
    current_user: CurrentUserRead,
    show_all: bool = False,
    session: AsyncSession = Depends(get_async_session),
) -> CafeInfo:
    """Получить кафе по ID.

    Доступ к неактивным кафе регулируется policy:
    - для некоторых ролей show_all=True запрещён,
    - для MANAGER действует ограничение “неактивные только свои”.

    Возвращает:
    - CafeInfo, либо 404 если объект не найден/не доступен по фильтрам.
    """
    ctx = policy.read_context(current_user=current_user, show_all=show_all)
    return await crud_cafe.get(
        session,
        cafe_id=cafe_id,
        active_objects_only=ctx.active_objects_only,
        where_expr=ctx.where_expr,
    )


@router.post('', response_model=CafeInfo, status_code=status.HTTP_201_CREATED)
async def create_cafe(
    cafe_data: CafeCreate,
    current_user: Annotated[
        User,
        Security(get_current_user, scopes=[Scopes.CAFES_WRITE.value]),
    ],
    session: AsyncSession = Depends(get_async_session),
) -> CafeInfo:
    """Создать новое кафе.

    Доступ:
    - scopes: требуется CAFES_WRITE (JWT).

    Возвращает:
    - созданное CafeInfo.
    """
    managers_id = await _validate_managers_ids(session, cafe_data.managers_id)

    return await crud_cafe.create(
        session,
        obj_in=cafe_data,
        managers_id=managers_id,
    )


@router.patch('/{cafe_id}', response_model=CafeInfo)
async def update_cafe(
    cafe_id: int,
    cafe_update: CafeUpdate,
    current_user: Annotated[
        User,
        Security(get_current_user, scopes=[Scopes.CAFES_UPDATE.value]),
    ],
    session: AsyncSession = Depends(get_async_session),
) -> CafeInfo:
    """Обновить кафе (PATCH).

    Правила:
    - scopes: требуется CAFES_UPDATE (JWT).
    - role-based ограничения на поля (например, managers_id/is_active
     только ADMIN)

    Возвращает:
    - обновлённое CafeInfo.
    """
    policy.assert_update_payload_allowed(current_user, cafe_update)

    where_expr = policy.update_where_expr(current_user)

    data = cafe_update.model_dump(exclude_unset=True)

    managers_id: list[int] | None = None
    if current_user.role == UserRole.ADMIN and 'managers_id' in data:
        managers_id = await _validate_managers_ids(session, data.pop('managers_id') or [])

    return await crud_cafe.update(
        session,
        cafe_id=cafe_id,
        data=data,
        managers_id=managers_id,
        active_objects_only=False,
        # чтобы не получать 404 на неактивных при update
        where_expr=where_expr,
    )
