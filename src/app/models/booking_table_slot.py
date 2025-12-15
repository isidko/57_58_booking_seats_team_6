from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import IntIDPKModel

if TYPE_CHECKING:
    from app.models import Booking, Slot, Table


class BookingTableSlot(IntIDPKModel):
    """Промежуточная модель для связи бронирования, стола и слота."""

    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('bookings.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    table_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tables.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    slot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('slots.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            'booking_id', 'table_id', 'slot_id', name='uq_booking_table_slot',
        ),
    )
    booking: Mapped['Booking'] = relationship(
        'Booking',
        back_populates='booking_table_slots',
    )
    table: Mapped['Table'] = relationship(
        'Table',
        back_populates='booking_table_slots',
        lazy='joined',
    )
    slot: Mapped['Slot'] = relationship(
        'Slot',
        back_populates='booking_table_slots',
        lazy='joined',
    )

    def __repr__(self) -> str:
        return (
            f'BookingTableSlot(id={self.id}, '
            f'booking={self.booking_id}, '
            f'table={self.table_id}, '
            f'slot={self.slot_id})'
        )
