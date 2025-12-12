from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe


class Table(AbstractIntIDModel):
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment='Описание'
    )
    seat_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='Количество посадочных мест'
    )
    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
        nullable=False,
        index=True,
        comment='ID кафе'
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='tables',
        lazy='joined'
    )

    __table_args__ = (
        CheckConstraint(
            'seat_number > 0 AND seat_number < 20',
            name='check_seat_number_positive_and_lt_max_seat_number'
        )
    )

    def __repr__(self) -> str:
        return (
            f'{self.id=}, '
            f'{self.seat_number=}, '
            f'{self.cafe_id=}, '
            f'{super().__repr__()}'
        )
