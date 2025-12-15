from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CAFE_MAX_SEAT_NUMBER, CAFE_MIN_SEAT_NUMBER
from app.models.base import IntIDPKModel, TimestampedActiveModel

if TYPE_CHECKING:
    from app.models import BookingTableSlot, Cafe


class Table(TimestampedActiveModel, IntIDPKModel):
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
        ForeignKey('cafes.id', ondelete='CASCADE'),
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
        cascade='save-update, merge, delete',
        passive_deletes=True,
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            (seat_number.between(CAFE_MIN_SEAT_NUMBER, CAFE_MAX_SEAT_NUMBER)),
            name='check_seat_number_positive_and_lt_max_seat_number',
        )
    )

    def __repr__(self) -> str:
        return f'{self.id=}, {self.seat_number=}, {self.cafe_id=}.'
