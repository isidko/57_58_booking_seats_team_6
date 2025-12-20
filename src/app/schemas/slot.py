from datetime import date, datetime, time, timedelta
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator

from app.core.constants import SLOT_MIN_DURATION_MINUTES
from app.schemas.cafe import CafeShortInfo

MIN_SLOT_DURATION = timedelta(minutes=SLOT_MIN_DURATION_MINUTES)

StartTime = Annotated[
    time,
    Field(
        ...,
        description='Время начала временного слота',
        examples=['10:00'],
    ),
]

EndTime = Annotated[
    time,
    Field(
        ...,
        description='Время окончания временного слота',
        examples=['12:00'],
    ),
]

IsActive = Annotated[
    bool,
    Field(
        ...,
        description='Флаг активности временного слота',
        examples=[True],
    ),
]


def _validate_slot_time_range(
    start_time: time,
    end_time: time,
) -> None:
    """Проверяет корректность временного диапазона слота.

    - время окончания позже времени начала
    - минимальную длительность слота
    """
    if end_time <= start_time:
        raise ValueError(
            'Время окончания временного слота '
            'должно быть позже времени начала.',
        )

    start_dt = datetime.combine(date.min, start_time)
    end_dt = datetime.combine(date.min, end_time)

    if end_dt - start_dt < MIN_SLOT_DURATION:
        raise ValueError(
            f'Минимальная длительность временного слота — '
            f'{SLOT_MIN_DURATION_MINUTES} минут.',
        )


class SlotBase(BaseModel):
    """Базовая схема временного слота."""

    description: str | None = Field(
        None,
        description='Описание временного слота',
        examples=['Утренний слот'],
    )

    model_config = ConfigDict(extra='forbid')


class SlotCreate(SlotBase):
    """Создание временного слота."""

    start_time: StartTime
    end_time: EndTime

    @model_validator(mode='after')
    def validate_slot_time_range(self) -> Self:
        """Проверяет корректность временного диапазона слота."""
        _validate_slot_time_range(self.start_time, self.end_time)
        return self


class SlotUpdate(SlotBase):
    """Обновление временного слота - все поля Optional."""

    start_time: StartTime | None = None
    end_time: EndTime | None = None
    is_active: IsActive | None = None

    @model_validator(mode='after')
    def validate_slot_time_range(self) -> Self:
        """Проверяет корректность временного диапазона слота."""
        if self.start_time is not None and self.end_time is not None:
            _validate_slot_time_range(self.start_time, self.end_time)
        return self

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "start_time": "11:00",
                "end_time": "14:00",
                "description": "Обновленный дневной слот",
                "is_active": False,
            },
        },
    )


class SlotShortInfo(SlotBase):
    """Короткая информация о временном слоте."""

    id: PositiveInt = Field(
        ...,
        description='ID временного слота',
        examples=[1],
    )
    start_time: StartTime
    end_time: EndTime

    model_config = ConfigDict(from_attributes=True)


class SlotInfo(SlotShortInfo):
    """Полная информация о временном слоте."""

    cafe: CafeShortInfo = Field(
        ...,
        description='Информация о кафе',
    )
    is_active: IsActive
    created_at: datetime = Field(
        ...,
        description='Дата и время создания записи',
        examples=['2025-12-19T06:00:27Z'],
    )
    updated_at: datetime = Field(
        ...,
        description='Дата и время последнего обновления записи',
        examples=['2025-12-19T06:00:27Z'],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "cafe": {
                    "id": 1,
                    "name": "Кофейня у моря",
                    "address": "ул. Приморская, 15",
                    "phone": "+79991234567",
                    "photo_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                },
                "start_time": "10:00",
                "end_time": "12:00",
                "description": "Утренний слот",
                "is_active": True,
                "created_at": "2025-12-19T06:00:27Z",
                "updated_at": "2025-12-19T06:00:27Z",
            },
        },
    )
