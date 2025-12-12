from typing import TYPE_CHECKING

from app.core.db import Base
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy import Table as SATable
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models import Slot, Table, User

# Ассоциативная таблица для связи многие-ко-многим
cafe_managers = SATable(
    'cafe_managers',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True),
)


class Cafe(AbstractIntIDModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment='Название',
    )
    address: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment='Адрес',
    )
    phone: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
        comment='Телефон',
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
        comment='ID изображения',
    )
    managers: Mapped[list['User']] = relationship(
        'User',
        secondary=cafe_managers,
        back_populates='managed_cafes',
        lazy='selectin',
        cascade='save-update, merge',
    )
    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge',
        order_by='Table.seat_number',
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge',
        order_by='Slot.start_time',
    )

    def __repr__(self) -> str:
        return (
            f'{self.name=}, '
            f'{self.address=}, '
            f'{self.phone=}, '
            f'{super().__repr__()}'
        )
