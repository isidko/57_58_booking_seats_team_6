from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.slot import Slot
    from app.models.table import Table


class BookingTableSlot(AbstractIntIDModel):
    """Промежуточная модель для связи бронирования, стола и слота."""

    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('bookings.id'),
        nullable=False,
        index=True,
    )
    table_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tables.id'),
        nullable=False,
        index=True,
    )
    slot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('slots.id'),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            'booking_id',
            'table_id',
            'slot_id',
            name='uq_booking_table_slot',
        ),
    )
    booking: Mapped['Booking'] = relationship(
        'Booking',
        back_populates='table_slots',
    )
    table: Mapped['Table'] = relationship(
        'Table',
        lazy='joined',
    )
    slot: Mapped['Slot'] = relationship(
        'Slot',
        lazy='joined',
    )

    def __repr__(self) -> str:
        return f'<BookingTableSlot(id={self.id}, booking={self.booking_id})>'

    def to_response_dict(self) -> dict:
        """Конвертация в формат ответа API."""
        return {
            'id': self.id,
            'table': {
                'id': self.table.id,
                'description': self.table.description,
                'seat_number': self.table.seat_number,
                'is_active': self.table.is_active,
            },
            'slot': {
                'id': self.slot.id,
                'start_time': self.slot.start_time.isoformat(),
                'end_time': self.slot.end_time.isoformat(),
                'description': self.slot.description,
                'is_active': self.slot.is_active,
            },
        }
