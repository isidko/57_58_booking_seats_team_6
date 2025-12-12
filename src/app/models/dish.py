from typing import TYPE_CHECKING

from app.core.db import Base
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe


# Ассоциативная таблица для связи многие-ко-многим
dish_cafes = Table(
    'dish_cafes',
    Base.metadata,
    Column('dish_id', ForeignKey('dishes.id'), primary_key=True),
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
)


class Dish(AbstractIntIDModel):
    """Модель блюда."""

    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment='Название',
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Описание',
    )
    photo_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('photo.id'),
        nullable=False,
        index=True,
        comment='ID изображения',
    )
    price: Mapped[Numeric] = mapped_column(
        Numeric(10, 2),  # 10 цифр, 2 после запятой
        nullable=False,
        comment='Цена',
    )
    cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary=dish_cafes,
        back_populates='dishes',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            'price > 0',
            name='check_positive_price',
        ),
    )

    def __repr__(self) -> str:
        return f'{self.name=}, {self.price=}, {super().__repr__()}'
