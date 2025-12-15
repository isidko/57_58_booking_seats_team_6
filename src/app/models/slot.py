from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import IntIDPKModel, TimestampedActiveModel

if TYPE_CHECKING:
    from app.models import BookingTableSlot, Cafe


class Slot(TimestampedActiveModel, IntIDPKModel):
    """Модель временного слота."""

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment='Время начала слота',
    )
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        comment='Время окончания слота',
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Описание',
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
        back_populates='slots',
        lazy='joined',
    )
    booking_table_slots: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        back_populates='slot',
        cascade='save-update, merge, delete',
        passive_deletes=True,
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint(
            (end_time > start_time), name='check_end_time_after_start_time',
        ),
    )

    def __repr__(self) -> str:
        return (
            f'{self.id=}, '
            f'{self.start_time=}, '
            f'{self.end_time=}, '
            f'{self.cafe_id=}.'
        )
