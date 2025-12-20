from datetime import datetime
from typing import Annotated, List, Self, TypeAlias
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator

from app.core.constants import (
    ADDRESS_MAX_LENGTH,
    ADDRESS_MIN_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    DESCRIPTION_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_MIN_LENGTH,
)
from app.schemas.user import UserShortInfo

Name: TypeAlias = Annotated[
    str,
    Field(
        ...,
        description='Название кафе',
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        examples=['Какое-то название кафе'],
    ),
]
Address: TypeAlias = Annotated[
    str,
    Field(
        ...,
        description='Адрес',
        min_length=ADDRESS_MIN_LENGTH,
        max_length=ADDRESS_MAX_LENGTH,
        examples=['ул. Какая-то, 40'],
    ),
]
Phone: TypeAlias = Annotated[
    str,
    Field(
        ...,
        description='Телефон',
        min_length=PHONE_MIN_LENGTH,
        max_length=PHONE_MAX_LENGTH,
        examples=['+79876543210'],
    ),
]

PhotoId: TypeAlias = Annotated[
    UUID,
    Field(
        ...,
        description='ID изображения',
        examples=['50c42bd2-615e-4fec-a325-0e5c4d3d73d3'],
    ),
]

ManagersId: TypeAlias = Annotated[
    List[PositiveInt],
    Field(
        ...,
        description='Список ID менеджеров',
        examples=[[1, 2]],
        min_length=1,
    ),
]


class CafeBase(BaseModel):
    """Общие поля кафе для create/update."""

    description: str | None = Field(
        None,
        description='Описание',
        min_length=DESCRIPTION_MIN_LENGTH,
        max_length=DESCRIPTION_MAX_LENGTH,
        examples=['Русская кухня'],
    )


class CafeBaseRequiredFields(CafeBase):
    """Общие поля кафе для create/shortinfo."""

    name: Name
    address: Address
    phone: Phone
    photo_id: PhotoId


class CafeCreate(CafeBaseRequiredFields):
    """Body для POST /cafes."""

    managers_id: ManagersId


class CafeUpdate(CafeBase):
    """Body для PATCH /cafes/{cafeid} (частичное обновление)."""

    name: Name | None = None
    address: Address | None = None
    phone: Phone | None = None
    photo_id: PhotoId | None = None
    managers_id: ManagersId | None = None

    is_active: bool | None = Field(
        None,
        description='Флаг активности',
        examples=[False],
    )

    @model_validator(mode='after')
    def validate_body_cafe_update(self) -> Self:
        """Проверяет наличие как минимум одного поля при обновлении."""
        if not self.model_fields_set:
            raise ValueError('Пустой запрос не разрешён')
        return self


class CafeShortInfo(CafeBaseRequiredFields):
    """Короткая информация о кафе."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class CafeInfo(CafeShortInfo):
    """Полная инфа о кафе."""

    managers: list[UserShortInfo]
    is_active: bool = Field(
        ...,
        description='Флаг активности',
        examples=[True],
    )
    created_at: datetime = Field(
        ...,
        description='Дата и время создания записи',
    )
    updated_at: datetime = Field(
        ...,
        description='Дата и время последнего обновления записи',
    )
