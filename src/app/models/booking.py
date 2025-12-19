from datetime import date
from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import IntIDPKModel, TimestampedActiveModel

if TYPE_CHECKING:
    from app.models import BookingTableSlot, Cafe, User


class BookingStatus(IntEnum):
    """Статусы бронирования как числовой Enum."""

    OPEN = 0          # Открыто
    ACTIVE = 1        # Активно
    CANCELLED = 2     # Закрыто


class Booking(TimestampedActiveModel, IntIDPKModel):
    """Модель бронирования."""

    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment='ID кафе',
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
        index=True,
        comment='ID пользователя',
    )
    guest_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Количество гостей',
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Заметка',
    )
    status: Mapped[BookingStatus] = mapped_column(
        Integer,
        nullable=False,
        default=BookingStatus.OPEN,
        index=True,
        comment='Статус бронирования',
    )
    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment='Дата бронирования',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='bookings',
        lazy='selectin',
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='bookings',
        lazy='selectin',
    )
    booking_table_slots: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        back_populates='booking',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            (guest_number > 0), name='check_guest_number_higher_then_0',
        ),
        CheckConstraint(
            (status.in_([0, 1, 2])), name='check_booking_status_range',
        ),
        UniqueConstraint(
            'user_id', 'booking_date', 'cafe_id', name='uq_user_date_cafe',
        ),
    )

    def __repr__(self) -> str:
        return (
            f'{self.cafe_id=}, '
            f'{self.guest_number=}, '
            f'{self.booking_date=}, '
            f'{self.status=}.'
        )
