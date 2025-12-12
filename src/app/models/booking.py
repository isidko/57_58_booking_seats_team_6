from datetime import date
from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import AbstractIntIDModel

if TYPE_CHECKING:
    from app.models import BookingTableSlot, Cafe, User


class BookingStatus(IntEnum):
    """Статусы бронирования как числовой Enum."""

    OPEN = 0  # Открыто
    ACTIVE = 1  # Активно
    CANCELLED = 2  # Закрыто

    # Для обратной совместимости со строковыми значениями
    @classmethod
    def from_string(cls, value: str) -> 'BookingStatus':
        """Конвертировать строку в Enum."""
        mapping = {
            'open': cls.OPEN,
            'active': cls.ACTIVE,
            'cancelled': cls.CANCELLED,
        }
        return mapping.get(value.lower(), cls.OPEN)

    def to_string(self) -> str:
        """Конвертировать Enum в строку."""
        mapping = {
            self.OPEN: 'open',
            self.ACTIVE: 'active',
            self.CANCELLED: 'cancelled',
        }
        return mapping[self]

    @property
    def display_name(self) -> str:
        """Человеко-читаемое название."""
        names = {
            self.OPEN: 'Открыто',
            self.ACTIVE: 'Активно',
            self.CANCELLED: 'Закрыто',
        }
        return names[self]


class Booking(AbstractIntIDModel):
    """Модель бронирования."""

    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
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
        description='Количество гостей',
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
        lazy='joined',
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='bookings',
        lazy='joined',
    )
    table_slots: Mapped[list['BookingTableSlot']] = relationship(
        'BookingTableSlot',
        back_populates='booking',
        cascade='save-update, merge',
        lazy='selectin',
    )

    @property
    def tables_slots_response(self) -> list[dict]:
        """Форматированный список столиков и слотов для API."""
        return [
            {
                'id': table_slot.id,
                'table': {
                    'id': table_slot.table.id,
                    'description': table_slot.table.description,
                    'seat_number': table_slot.table.seat_number,
                },
                'slot': {
                    'id': table_slot.slot.id,
                    'start_time': table_slot.slot.start_time.isoformat(),
                    'end_time': table_slot.slot.end_time.isoformat(),
                    'description': table_slot.slot.description,
                },
            }
            for table_slot in self.table_slots
            if table_slot.table.is_active and table_slot.slot.is_active
        ]

    @property
    def customer_info(self) -> dict:
        """Информация о клиенте."""
        return {
            'id': self.user.id,
            'name': self.user.full_name,
            'phone': self.user.phone,
            'email': self.user.email,
        }

    def to_response_dict(self) -> dict:
        """Конвертация в формат ответа API."""
        return {
            'id': self.id,
            'cafe_id': self.cafe_id,
            'guest_number': self.guest_number,
            'booking_date': self.booking_date.isoformat(),
            'note': self.note,
            'status': self.status.value,
            'status_display': self.status.display_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            'is_active': self.is_active,
            'customer': self.customer_info,
            'tables_slots': self.tables_slots_response,
        }

    def __repr__(self) -> str:
        return (
            f'{self.cafe_id=}, '
            f'{self.guest_number=}, '
            f'{self.booking_date=}, '
            f'{self.status=}, '
            f'{super().__repr__()}'
        )
