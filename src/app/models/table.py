from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TimestampedActiveIntIDModel

if TYPE_CHECKING:
    from app.models import BookingTableSlot, Cafe


class Table(TimestampedActiveIntIDModel):
    """Модель стола для бронирования."""

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Описание',
    )
    seat_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Количество посадочных мест',
    )
    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
        nullable=False,
        index=True,
        comment='ID кафе',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='tables',
        lazy='joined',
    )
    booking_table_slots: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        back_populates='table',
        cascade='save-update, merge',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            'seat_number BETWEEN 1 AND 20',
            name='check_seat_number_positive_and_lt_max_seat_number',
        )
    )

    def __repr__(self) -> str:
        return f'{self.id=}, {self.seat_number=}, {self.cafe_id=}.'
