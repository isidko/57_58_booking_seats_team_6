"""__init__.py импортирует Cafe из cafe.py.

cafe.py импортировал из app.models (то есть из __init__.py)
Это создает циклический импорт.

Поэтому тут используем прямой импорт, а не относительный!
from app.models.cafe_manager import cafe_managers  etc.
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    ADDRESS_MAX_LENGTH,
    ADDRESS_MIN_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
    PHONE_MAX_LENGTH,
)
from app.models.base import IntIDPKModel, TimestampedActiveModel
from app.models.cafe_manager import cafe_managers
from app.models.dish_cafe import dish_cafes

if TYPE_CHECKING:
    from app.models import Booking, Dish, Slot, Table, User


class Cafe(TimestampedActiveModel, IntIDPKModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH),
        nullable=False,
        index=True,
        comment='Название',
    )
    address: Mapped[str] = mapped_column(
        String(ADDRESS_MAX_LENGTH),
        nullable=False,
        comment='Адрес',
    )
    phone: Mapped[str] = mapped_column(
        String(PHONE_MAX_LENGTH),
        nullable=False,
        comment='Телефон',
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Описание',
    )
    photo_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('photos.id', ondelete='SET NULL'),
        nullable=True,
        comment='ID изображения',
    )
    dishes: Mapped[list['Dish']] = relationship(
        'Dish',
        secondary=dish_cafes,
        lazy='raise_on_sql',
    )
    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='cafe',
        lazy='raise_on_sql',
    )
    managers: Mapped[list['User']] = relationship(
        'User',
        secondary=cafe_managers,
        lazy='selectin',
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        back_populates='cafe',
        lazy='raise_on_sql',
    )
    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        lazy='raise_on_sql',
    )

    __table_args__ = (
        CheckConstraint(
            func.char_length(name) > NAME_MIN_LENGTH,
            name='ck_cafe_name_min_length',
        ),
        CheckConstraint(
            func.char_length(address) > ADDRESS_MIN_LENGTH,
            name='ck_cafe_address_min_length',
        ),
        CheckConstraint(
            phone.regexp_match("^\\+?[1-9]\\d{4,}$"),
            name='ck_cafe_phone_format',
        ),
        CheckConstraint(
            'LENGTH(TRIM(phone)) >= 5', name='ck_cafe_phone_min_length',
        ),
    )

    def __repr__(self) -> str:
        return f'{self.name=}, {self.address=}, {self.phone=}.'
