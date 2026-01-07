import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.cafe import cafe_crud  # noqa
from app.crud.slot import slot_crud  # noqa
from app.crud.table import table_crud  # noqa
from app.exceptions.common import (
    CommonDBValidationError,
    ObjectDoesNotBelongToAnotherObject,
    ObjectDoesNotExist,
    ObjectIsNotActive,
)
from app.models import Booking, BookingTableSlot, Cafe, Slot, Table


async def check_slot_exists(
        session: AsyncSession,
        slot_id: int,
) -> Slot:
    """Проверяем существование этого слота.

    :return Slot
    """
    slot = await slot_crud.get_by_pk(session=session, pk=slot_id)
    if not slot:
        raise ObjectDoesNotExist(
            message=f"This slot {slot_id} does not exist!",
        )
    if not slot.is_active:
        raise ObjectIsNotActive(message=f"This slot {slot_id} inactive!")
    return slot


async def check_cafe_exists(
        session: AsyncSession,
        cafe_id: int,
) -> Cafe:
    """Проверяем существование этого кафе.

    :return Cafe
    """
    cafe = await cafe_crud.get_by_pk(session=session, pk=cafe_id)
    if not cafe:
        raise ObjectDoesNotExist(
            message=f"This cafe {cafe_id} does not exist!",
        )
    if not cafe.is_active:
        raise ObjectIsNotActive(message=f"This cafe {cafe_id} inactive!")
    return cafe


async def check_table_exists(
        session: AsyncSession,
        table_id: int,
) -> Table:
    """Проверяем существование этого стола.

    :return Table
    """
    table = await table_crud.get_by_pk(session=session, pk=table_id)
    if not table:
        raise ObjectDoesNotExist(
            message=f"This table {table_id} does not exist!")
    if not table.is_active:
        raise ObjectIsNotActive(message=f"This table {table_id} inactive!")
    return table


def check_table_belongs_to_cafe(
        table: Table,
        cafe: Cafe,
) -> None:
    """Проверяем принадлежит ли этот стол этому кафе."""
    if not table.cafe.id == cafe.id:
        raise ObjectDoesNotBelongToAnotherObject(
            message=(
                f"This table: {table.id} "
                f"does not belong to this cafe: {cafe.id}"
            ),
        )


def check_slot_belongs_to_cafe(
        slot: Slot,
        cafe: Cafe,
) -> None:
    """Проверяем принадлежит ли этот слот этому кафе."""
    if not slot.cafe.id == cafe.id:
        raise ObjectDoesNotBelongToAnotherObject(
            message=(
                f"This slot: {slot.id} "
                f"does not belong to this cafe: {cafe.id}"
            ),
        )


async def check_this_table_and_slot_are_free_for_this_date(
        session: AsyncSession,
        slot: Slot,
        table: Table,
        booking_date: datetime.date,
) -> None:
    """Проверяем, нет ли уже активного booking на этот слот, кафе и дату."""
    query = select(BookingTableSlot.booking_id).join(
        Booking, Booking.id == BookingTableSlot.booking_id,
    ).where(
        BookingTableSlot.table_id == table.id,
        BookingTableSlot.slot_id == slot.id,
        Booking.booking_date == booking_date,
        Booking.is_active.is_(True),
        )
    intersections = (await session.execute(query)).scalars().first()
    if intersections:
        raise CommonDBValidationError(
            message=(
                f"This table {table.id} "
                f"and slot {slot.id} already booked!"
            ),
        )
