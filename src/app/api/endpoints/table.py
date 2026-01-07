from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.api.validators import check_table_belongs_to_cafe, check_table_exists
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.core.log_level import LogLevel
from app.core.logging import log_message
from app.crud.cafe import cafe_crud
from app.crud.table import table_crud
from app.exceptions.api import ForbiddenError
from app.exceptions.common import ObjectDoesNotExist
from app.models import Cafe, Table, User
from app.models.user import UserRole
from app.schemas.table import TableCreate, TableInfo, TableUpdate

router = APIRouter()


async def check_cafe_exists(
        session: AsyncSession,
        cafe_id: int,
) -> Cafe:
    """Проверяем существование этого кафе.

    :return Cafe
    """
    cafe = await cafe_crud.get_by_pk(session=session, obj_id=cafe_id)
    if not cafe:
        raise ObjectDoesNotExist(message=f'Кафе ID={cafe_id} не найдено!')
    return cafe


def is_owned_cafe(cafe: Cafe, user_id: int) -> bool:
    """Проверяем, что пользователь является менеджером кафе."""
    return any(manager.id == user_id for manager in cafe.managers)


@router.get(
    '/cafe/{cafe_id}/tables',
    response_model=list[TableInfo],
    summary='Получить список столов кафе',
    description=(
        'Возвращает список столов для указанного кафе. '
        'USER всегда видит только активные столы. '
        'MANAGER и ADMIN видят все столы при show_all=True, '
        'иначе только активные.'
    ),
)
async def list_table(
    cafe_id: int = Path(
        ...,
        description='ID кафе, для которого запрашивается список столов',
        ge=1,
        example=1,
    ),
    show_all: Annotated[bool, Query(
        description=(
            'Показывать все столы в кафе или только активные. '
            'Для USER игнорируется. По умолчанию True.'
        ),
    )] = True,
    session: AsyncSession = Depends(get_async_session),
    user: User = Security(get_current_user, scopes=[Scopes.TABLES_READ]),
) -> list[TableInfo]:
    """Получить список столов кафе."""
    log_message(
        message=f'Запрос столов кафе ID={cafe_id}, show_all={show_all}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )
    # Проверяем существование кафе по его ID
    cafe = await check_cafe_exists(session, cafe_id)

    # Возвращаем результат в зависимости от роли пользователя
    if user.role == UserRole.ADMIN or is_owned_cafe(cafe, user.id):
        return await table_crud.get_multi(
            session=session,
            active_objects_only=not show_all,
            where_expr=Table.cafe_id == cafe_id,
        )
    return await table_crud.get_multi(
        session=session,
        active_objects_only=True,
        where_expr=Table.cafe_id == cafe_id,
    )


@router.post(
    '/cafe/{cafe_id}/tables',
    response_model=TableInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новый стол в кафе',
    description='Создает новый стол для указанного кафе',
)
async def create_table(
    cafe_id: int = Path(
        ...,
        description='ID кафе, в котором создается стол',
        ge=1,
        example=1,
    ),
    table_in: TableCreate = Body(
        ...,
        description='Данные для создание стола',
        example={
            'description': 'Столик для двоих',
            'seat_number': 2,
        },
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Security(get_current_user, scopes=[Scopes.TABLES_WRITE]),
) -> TableInfo:
    """Создать новый стол в кафе."""
    log_message(
        message=f'Создание стола в кафе ID={cafe_id}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )
    # Проверяем существование кафе по его ID
    cafe = await check_cafe_exists(session, cafe_id)

    if not (user.role == UserRole.ADMIN or is_owned_cafe(cafe, user.id)):
        raise ForbiddenError(message='Доступ запрещен.')
    new_table = await table_crud.create(session, table_in, cafe_id=cafe.id)
    log_message(
        message=f'Создан стол ID={new_table.id} в кафе ID={cafe_id}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )

    new_table.cafe = cafe

    return TableInfo.model_validate(new_table)


@router.get(
    '/cafe/{cafe_id}/tables/{table_id}',
    response_model=TableInfo,
    summary='Получить информацию о столе',
    description='Возвращает полную информацию о конкретном столе кафе',
)
async def get_table(
    cafe_id: int = Path(
        ...,
        description='ID кафе, которому принадлежит стол',
        ge=1,
        example=1,
    ),
    table_id: int = Path(
        ...,
        description='ID стола, о котором запрашивается информация',
        ge=1,
        example=2,
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Security(get_current_user, scopes=[Scopes.TABLES_READ]),
) -> TableInfo:
    """Получить информацию о конкретном столе."""
    log_message(
        message=f'Запрос информации о столе ID={table_id} в кафе ID={cafe_id}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )
    # Проверяем существование кафе по его ID
    cafe = await check_cafe_exists(session, cafe_id)

    # Возвращаем результат в зависимости от роли пользователя
    if user.role == UserRole.ADMIN or is_owned_cafe(cafe, user.id):
        table = await table_crud.get_by_pk(session, table_id)
    else:
        table = await check_table_exists(session, table_id)
    log_message(
        message=f'Возврат информации о столе ID={table.id} кафе ID={cafe.id}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )
    return TableInfo.model_validate(table)


@router.patch(
    '/cafe/{cafe_id}/tables/{table_id}',
    response_model=TableInfo,
    summary='Обновить информацию о столе',
    description='Обновляет информацию о столе (частичное обновление)',
)
async def update_table(
    cafe_id: int = Path(
        ...,
        description='ID кафе, которому принадлежит стол',
        ge=1,
        example=1,
    ),
    table_id: int = Path(
        ...,
        description='ID стола, о котором обновляется информация',
        ge=1,
        example=2,
    ),
    table_in: TableUpdate = Body(
        ...,
        description='Данные для обновления информации о столе',
        example={
            'description': 'Столик для двоих',
            'seat_number': 2,
            'is_active': True,
        },
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Security(get_current_user, scopes=[Scopes.TABLES_UPDATE]),
) -> TableInfo:
    """Обновить информацию о столе."""
    log_message(
        message=f'Обновление стола ID={table_id} в кафе ID={cafe_id}',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )
    # Проверяем существование кафе по его ID
    cafe = await check_cafe_exists(session, cafe_id)

    # Проверяем права пользователя
    if not (user.role == UserRole.ADMIN or is_owned_cafe(cafe, user.id)):
        log_message(
            message='Попытка изменения без прав доступа',
            level=LogLevel.WARNING,
            username=user.username,
            user_id=user.id,
        )
        raise ForbiddenError(message='Доступ запрещен.')

    # Получаем стол
    table = await table_crud.get_by_pk(session, table_id)

    if not table:
        log_message(
            message=f'Стол ID={table_id} не найден',
            level=LogLevel.WARNING,
            username=user.username,
            user_id=user.id,
        )
        raise ObjectDoesNotExist(message='Стол ID={table_id} не найден')

    # Проверяем, что стол принадлежит кафе
    check_table_belongs_to_cafe(table, cafe)

    updated_table = await table_crud.update(
        session=session,
        db_obj=table,
        obj_in=table_in,
    )
    log_message(
        message=f'Стол {table_id} успешно обновлен',
        level=LogLevel.INFO,
        username=user.username,
        user_id=user.id,
    )

    return TableInfo.model_validate(updated_table)
