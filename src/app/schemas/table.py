from typing import Annotated, Self, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator

from app.core.constants import CAFE_MAX_SEAT_NUMBER, CAFE_MIN_SEAT_NUMBER
from app.schemas.cafe import CafeShortInfo
from app.schemas.common import TimestampedActiveSchema

Description: TypeAlias = Annotated[
    str,
    Field(description='Описание стола', examples=['Столик для двоих']),
]

Id: TypeAlias = Annotated[
    int,
    Field(..., description='ID стола', examples=[1]),
]

SeatNumber: TypeAlias = Annotated[
    PositiveInt,
    Field(
        description='Количество посадочных мест',
        ge=CAFE_MIN_SEAT_NUMBER,
        le=CAFE_MAX_SEAT_NUMBER,
        examples=[2],
    ),
]


class TableBase(BaseModel):
    """Базовая схема с общими полями."""

    description: Description | None = None
    seat_number: SeatNumber | None = None

    model_config = ConfigDict(extra='forbid')


class TableCreate(TableBase):
    """Создание стола."""

    seat_number: SeatNumber


class TableInfo(TableBase, TimestampedActiveSchema):
    """Полная информация о столе."""

    id: Id
    cafe: CafeShortInfo = Field(..., description='Информация о кафе')
    seat_number: SeatNumber

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
                    "description": "Уютная кофейня с видом на море",
                    "photo_id": "123e4567-e89b-12d3-a456-426614174000",
                },
                "description": "Столик для двоих",
                "seat_number": 2,
                "is_active": True,
                "created_at": "2025-05-15T10:30:00Z",
                "updated_at": "2025-05-20T10:30:00Z",
            },
        },
    )


class TableShortInfo(BaseModel):
    """Короткая информация о столе."""

    id: Id
    description: Description | None = None
    seat_number: SeatNumber

    model_config = ConfigDict(from_attributes=True)


class TableUpdate(TableBase):
    """Обновление стола - все поля Optional."""

    is_active: bool = Field(
        None,
        description='Флаг активности (не может быть null)',
        examples=[False],
    )
    seat_number: SeatNumber = None

    @model_validator(mode='after')
    def validate_at_least_one_field(self) -> Self:
        """Проверяем, что хотя бы одно поле предоставлено для обновления."""
        if not self.model_fields_set:
            raise ValueError('Пустой запрос не разрешён')
        return self

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "description": "Обновленное описание",
                "seat_number": 4,
                "is_active": False,
            },
        },
    )
