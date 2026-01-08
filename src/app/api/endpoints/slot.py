from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_active_user
from app.api.validators import (
    check_cafe_exists,
    check_slot_belongs_to_cafe,
)
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.crud.base import CRUDBase
from app.exceptions.common import ObjectDoesNotExist
from app.models import Cafe, Slot, User, UserRole
from app.schemas.slot import SlotCreate, SlotInfo, SlotUpdate

router = APIRouter()

slot_crud_base = CRUDBase[Slot, SlotCreate, SlotUpdate](Slot)


@router.get(
    '/cafe/{cafe_id}/time_slots',
    response_model=list[SlotInfo],
)
async def list_slot(
    *,
    cafe_id: int = Path(...),
    show_all: Annotated[bool, Query(
        description=(
            'Показывать все слоты в кафе или только активные. '
            'Для USER игнорируется. '
            'По умолчанию возвращаются только активные.'
        ),
    )] = False,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(
        get_current_active_user,
        scopes=[Scopes.TIME_SLOTS_READ],
    ),
) -> Any:
    """Получить слоты в кафе.

    Для ролей ADMIN и MANAGER - все слоты или только активные.
    Для пользователя (USER) - только активные.
    """
    await check_cafe_exists(session=session, cafe_id=cafe_id)

    if current_user.role == UserRole.USER:
        return await slot_crud_base.get_multi(
            session=session,
            where_expr=Slot.cafe_id == cafe_id,
        )

    return await slot_crud_base.get_multi(
        session=session,
        where_expr=Slot.cafe_id == cafe_id,
        active_objects_only=not show_all,
    )


@router.post(
    '/cafe/{cafe_id}/time_slots',
    response_model=SlotInfo,
)
async def create_slot(
    *,
    cafe_id: int = Path(...),
    slot_in: SlotCreate,
    session: AsyncSession = Depends(get_async_session),
    _ : User = Security(
        get_current_active_user,
        scopes=[Scopes.TIME_SLOTS_WRITE],
    ),
) -> Any:
    """Создать слот в кафе.

    Доступно только для ролей ADMIN и MANAGER.
    """
    await check_cafe_exists(session=session, cafe_id=cafe_id)

    return await slot_crud_base.create(
        session=session,
        obj_in=slot_in,
        cafe_id=cafe_id,
    )


@router.get(
    '/cafe/{cafe_id}/time_slots/{slot_id}',
    response_model=SlotInfo,
)
async def get_slot(
    *,
    cafe_id: int = Path(...),
    slot_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(
        get_current_active_user,
        scopes=[Scopes.TIME_SLOTS_READ],
    ),
) -> Any:
    """Получить слот в кафе.

    Для ролей ADMIN и MANAGER - все слоты.
    Для пользователя (USER) - только активные.
    """
    cafe: Cafe = await check_cafe_exists(session=session, cafe_id=cafe_id)

    slot: Slot | None = await session.get(Slot, slot_id)
    if not slot:
        raise ObjectDoesNotExist(
            message=f"This slot {slot_id} does not exist!",
        )

    check_slot_belongs_to_cafe(slot=slot, cafe=cafe)

    # USER не видит неактивные слоты
    if current_user.role == UserRole.USER and not slot.is_active:
        raise ObjectDoesNotExist(
            message=f"This slot {slot_id} does not exist!",
        )
    return slot


@router.patch(
    '/cafe/{cafe_id}/time_slots/{slot_id}',
    response_model=SlotInfo,
)
async def update_slot(
    *,
    cafe_id: int = Path(...),
    slot_id: int = Path(...),
    slot_in: SlotUpdate,
    session: AsyncSession = Depends(get_async_session),
    _ : User = Security(
        get_current_active_user,
        scopes=[Scopes.TIME_SLOTS_UPDATE],
    ),
) -> Any:
    """Обновить слот в кафе.

    Доступно только для ролей ADMIN и MANAGER.
    """
    cafe: Cafe = await check_cafe_exists(session=session, cafe_id=cafe_id)

    slot: Slot | None = await session.get(Slot, slot_id)
    if not slot:
        raise ObjectDoesNotExist(
            message=f"This slot {slot_id} does not exist!",
        )

    check_slot_belongs_to_cafe(slot=slot, cafe=cafe)

    return await slot_crud_base.update(
        session=session,
        db_obj=slot,
        obj_in=slot_in,
    )
