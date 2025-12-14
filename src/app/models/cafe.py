from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TimestampedActiveIntIDModel

if TYPE_CHECKING:
    from app.models import Booking, CafeManager, Dish, Slot, Table


class Cafe(TimestampedActiveIntIDModel):
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
    dishes: Mapped[list['Dish']] = relationship(
        'Dish',
        secondary='dishcafes',
        back_populates='cafes',
        lazy='selectin',
        cascade='save-update, merge',
    )
    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='cafe',
        cascade='save-update, merge',
        lazy='selectin',
        order_by='Booking.booking_date.desc()',
    )
    cafe_managers: Mapped[list['CafeManager']] = relationship(
        'CafeManager',
        back_populates='cafe',
        cascade='save-update, merge',
        lazy='selectin',
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge',
        order_by='Slot.start_time',
    )
    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge',
        order_by='Table.seat_number',
    )

    __table_args__ = (
        CheckConstraint(
            'LENGTH(TRIM(name)) >= 2', name='ck_cafe_name_min_length',
        ),
        CheckConstraint(
            'LENGTH(TRIM(address)) >= 5', name='ck_cafe_address_min_length',
        ),
        CheckConstraint(
            "phone ~ '^\\+?[1-9]\\d{4,}$'", name='ck_cafe_phone_format',
        ),
        CheckConstraint(
            'LENGTH(TRIM(phone)) >= 5', name='ck_cafe_phone_min_length',
        ),
    )

    def __repr__(self) -> str:
        return (
            f'{self.name=}, '
            f'{self.address=}, '
            f'{self.phone=}, '
            f'{super().__repr__()}'
        )
