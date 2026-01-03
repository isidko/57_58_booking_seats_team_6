import datetime
from typing import Annotated, Self, TypeAlias

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FutureDate,
    PositiveInt,
    model_validator,
)

from ..core.constants import (
    GUEST_NUMBER_MAX,
    GUEST_NUMBER_MIN,
    NOTE_MAX_LENGTH,
)
from .cafe import CafeShortInfo
from .common import TimestampedActiveSchema
from .table import TableShortInfo
from .timeslot import TimeSlotShortInfo  # noqa
from .user import UserShortInfo
from app.models.booking import BookingStatus

Note = Annotated[
    str,
    Field(
        ...,
        max_length=NOTE_MAX_LENGTH,
        description="Note for this booking",
        examples=['Book near the window'],
    ),
]

GuestNumber: TypeAlias = Annotated[
    PositiveInt,
    Field(
        ...,
        description='Количество гостей',
        ge=GUEST_NUMBER_MIN,
        le=GUEST_NUMBER_MAX,
        examples=[2],
    ),
]

Status: TypeAlias = Annotated[
    BookingStatus,
    Field(
        default=BookingStatus.OPEN,
        description='Статус бронирования',
        examples=[BookingStatus.OPEN],
    ),
]

TablesSlots: TypeAlias = Annotated[
    list['TableSlot'],
    Field(
        ...,
        description='Список столов и слотов для бронирования',
        examples=[[{'table_id': 1, 'slot_id': 1}]],
    ),
]

BookingDate: TypeAlias = Annotated[
    datetime.date,
    Field(
        ...,
        description='Дата бронирования',
        examples=['2024-01-01'],
    ),
]


class TableSlot(BaseModel):
    """Создание M2M между Slot и Table."""

    table_id: PositiveInt = Field(
        ...,
        description='ID стола',
        examples=[1],
    )
    slot_id: PositiveInt = Field(
        ...,
        description='ID слота',
        examples=[1],
    )


class TableSlotInfo(BaseModel):
    """Данные из БД для M2M TableSlot."""

    id: PositiveInt = Field(
        ...,
        description='ID связи стол-слот',
        examples=[1],
    )
    table: TableShortInfo
    slot: TimeSlotShortInfo

    model_config = ConfigDict(from_attributes=True)


class BookingBase(BaseModel):
    """Общие поля booking для create/update."""

    note: Note | None = None
    status: Status = BookingStatus.OPEN
    guest_number: GuestNumber
    tables_slots: TablesSlots


class BookingCreate(BookingBase):
    """Body для POST /booking."""

    cafe_id: PositiveInt
    booking_date: BookingDate


class BookingUpdate(BookingBase):
    """Body для PATCH /booking.

    Обратить внимание, здесь используется
    запрещение Null для некоторых полей, но разрешение Omit.

    status: Status = None
    Omit - разрешен, так как есть default
    Если status всё же пришёл, он должен быть строго типа Status.
    Status у нас required (см Annotated Status type).
    """

    cafe_id: PositiveInt = Field(
        None,
        description='ID кафе',
        examples=[1],
    )
    tables_slots: TablesSlots = None
    guest_number: GuestNumber = None
    status: Status = None
    booking_date: FutureDate = None
    is_active: bool = Field(
        None,
        description='Флаг активности',
        examples=[True],
    )

    @model_validator(mode='after')
    def validate_body_cafe_update(self) -> Self:
        """Проверяет наличие как минимум одного поля при обновлении."""
        if not self.model_fields_set:
            raise ValueError('Пустой запрос не разрешён')
        return self


class BookingInfo(BookingBase, TimestampedActiveSchema):
    """Body для GET /booking."""

    id: PositiveInt = Field(
        ...,
        description='ID бронирования',
        examples=[1],
    )
    user: UserShortInfo
    cafe: CafeShortInfo
    booking_date: BookingDate
    tables_slots: list[TableSlotInfo]

    model_config = ConfigDict(from_attributes=True)
