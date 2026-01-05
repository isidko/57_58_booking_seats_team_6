from typing import Any

from fastapi import APIRouter, Depends, Path, Query, Security
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_active_user
from app.api.validators import (
    check_cafe_exists,
    check_slot_belongs_to_cafe,
    check_slot_exists,
    check_table_belongs_to_cafe,
    check_table_exists,
    check_this_table_and_slot_are_free_for_this_date,
)
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.crud.booking import booking_crud
from app.crud.cafe import cafe_crud
from app.exceptions.database import DBObjectNotFoundError
from app.models import Booking, Cafe, Slot, Table, User
from app.models.user import UserRole
from app.schemas.booking import BookingCreate, BookingInfo, BookingUpdate
from app.utils.security import get_owned_by_pk

router = APIRouter()


@router.get('/',
            response_model=list[BookingInfo])
async def list_booking(
        *,
        active_objects_only: bool | None = Query(True, example=False),
        cafe_id: int | None = Query(None, ge=0),
        user_id: int | None = Query(None, ge=0),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Security(get_current_active_user,
                                      scopes=[Scopes.BOOKING_READ]),
) -> Any:
    """Получить бронирования.

    Для пользователя (USER) игнорируется всё, кроме идентификатора кафе.
    Для ролей ADMIN и MANAGER используются ВСЕ параметры запроса для фильтрации.
    """
    if current_user.role == UserRole.USER:
        return await booking_crud.get_bookings(
            session=session,
            cafe_id=cafe_id,
            user_id=current_user.id,
        )

    return await booking_crud.get_bookings(
        session=session,
        cafe_id=cafe_id,
        user_id=user_id,
        active_objects_only=active_objects_only,
    )


@router.post('/',
             response_model=BookingInfo)
async def create_booking(
        booking: BookingCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Security(get_current_active_user,
                                      scopes=[Scopes.BOOKING_WRITE]),
) -> Any:
    """Создать бронирование.

    Только для авторизованных пользователей.
    """
    # валидируем входные данные
    cafe: Cafe = await check_cafe_exists(session=session,
                                         cafe_id=booking.cafe_id)

    async with session.begin():
        # Заблокируем 2 таблицы от изменений вне этой транзакции (убираем race condition)
        await session.execute(text('LOCK TABLE bookings IN SHARE ROW EXCLUSIVE MODE'))
        await session.execute(text('LOCK TABLE booking_table_slots IN SHARE ROW EXCLUSIVE MODE'))

        for requested_table_slot in booking.booking_table_slots:
            slot: Slot = await check_slot_exists(session=session,
                                                 slot_id=requested_table_slot.slot_id)
            table: Table = await check_table_exists(session=session,
                                                    table_id=requested_table_slot.table_id)
            check_table_belongs_to_cafe(cafe=cafe, table=table)
            check_slot_belongs_to_cafe(slot=slot, cafe=cafe)
            await check_this_table_and_slot_are_free_for_this_date(
                session=session,
                slot=slot,
                table=table,
                booking_date=booking.booking_date,
            )
        db_obj: Booking = await booking_crud.create(session=session, obj_in=booking,
                                                        user_id=current_user.id)

    return db_obj


@router.get('/{booking_id}',
            response_model=BookingInfo)
async def get_booking(
        *,
        booking_id: int = Path(..., title='Booking id', example=5),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Security(get_current_active_user,
                                      scopes=[Scopes.BOOKING_READ]),
) -> Any:
    """Получить бронирование по ID.

    Для пользователя (USER) возвращает только принадлежащий ему объект
    Для ролей ADMIN и MANAGER возвращает независимо от владельца.
    """
    if current_user.role == UserRole.USER:
        booking: Booking = await get_owned_by_pk(
            model=Booking,
            session=session,
            object_pk=booking_id,
            user_instance=current_user,
        )
        return booking

    return await booking_crud.get_by_pk(session=session, pk=booking_id)


@router.patch('/{booking_id}',
              response_model=BookingInfo)
async def update_booking(
        booking_in: BookingUpdate,
        booking_id: int = Path(..., title='Booking id', example=5),
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Security(get_current_active_user,
                                      scopes=[Scopes.BOOKING_UPDATE]),
) -> BookingInfo:
    """Обновить бронирование.

    Для пользователя (USER) сначала проверяется владелец.
    Для ролей ADMIN и MANAGER эта проверка не выполняется.
    """
    # проверяем владельца
    if current_user.role == UserRole.USER:
        existing_booking: Booking = await get_owned_by_pk(
            model=Booking,
            session=session,
            object_pk=booking_id,
            user_instance=current_user,
        )
    else:
        existing_booking: Booking | None = await booking_crud.get_by_pk(
            session=session, pk=booking_id)
        if not existing_booking:
            raise DBObjectNotFoundError(message="This booking does not exist.")

    cafe: Cafe | None = None
    # проверяем каждый атрибут входных данных.
    if booking_in.cafe_id:
        cafe = await check_cafe_exists(session=session,
                                       cafe_id=booking_in.cafe_id)
    async with session.begin():
        # Заблокируем 2 таблицы от изменений вне этой транзакции (убираем race condition)
        await session.execute(text('LOCK TABLE bookings IN SHARE ROW EXCLUSIVE MODE'))
        await session.execute(text('LOCK TABLE booking_table_slots IN SHARE ROW EXCLUSIVE MODE'))

        if booking_in.booking_table_slots:
            existing_table_slot_ids = [(i.table_id, i.slot_id) for i in
                                       existing_booking.booking_table_slots]
            # если есть table_slot, для валидации должны достать кафе (если его еще нет)
            if not cafe:
                cafe = await cafe_crud.get_by_pk(session=session,
                                                 pk=existing_booking.cafe_id)

            for requested_table_slot in booking_in.booking_table_slots:
                slot: Slot = await check_slot_exists(session=session,
                                                     slot_id=requested_table_slot.slot_id)
                table: Table = await check_table_exists(session=session,
                                                        table_id=requested_table_slot.table_id)
                # проверяем, что пришедшие !== уже существующим
                if (requested_table_slot.table_id,
                    requested_table_slot.slot_id) not in existing_table_slot_ids:
                    # если не те же пришли, продолжаем проверки
                    check_table_belongs_to_cafe(cafe=cafe, table=table)
                    check_slot_belongs_to_cafe(slot=slot, cafe=cafe)
                    await check_this_table_and_slot_are_free_for_this_date(
                        session=session,
                        slot=slot,
                        table=table,
                        booking_date=(
                            booking_in.booking_date
                            if booking_in.booking_date
                            else existing_booking.booking_date
                        ),
                    )

        # остальное на уровне БД проверять не будем
        db_obj: BookingInfo = await booking_crud.update(session=session,
                                                    db_obj=existing_booking,
                                                    obj_in=booking_in)

        return db_obj
