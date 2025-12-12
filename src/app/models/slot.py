from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe


class Slot(AbstractIntIDModel):
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
        ForeignKey('cafes.id'),
        nullable=False,
        index=True,
        comment='ID кафе',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='slots',
        lazy='joined',
    )

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='check_end_time_after_start_time',
        ),
        CheckConstraint(
            'EXTRACT(HOUR FROM start_time) BETWEEN 0 AND 23',
            name='check_valid_start_time_hour',
        ),
        CheckConstraint(
            'EXTRACT(HOUR FROM end_time) BETWEEN 0 AND 23',
            name='check_valid_end_time_hour',
        ),
    )

    def __repr__(self) -> str:
        return (
            f'{self.id=}, '
            f'{self.start_time=}, '
            f'{self.end_time=}, '
            f'{self.cafe_id=}, '
            f'{super().__repr__()}'
        )
