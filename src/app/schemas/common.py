from datetime import datetime

from pydantic import BaseModel, Field


class TimestampedActiveSchema(BaseModel):
    """Базовая схема для полей created_at, updated_at и is_active."""

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
