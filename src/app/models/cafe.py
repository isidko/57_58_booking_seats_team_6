"""
cascade on the ORM level is being being used ONLY ON THE PARENT SIDE!
https://docs.sqlalchemy.org/en/20/orm/cascades.html
This means that we use the "cascade" in relationship only on the parent
table. Not on the child ones.

Table and Cafe.
Cafe has many tables =>
tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge, delete',
        passive_deletes=True, - this is used not to copy on the ORM level the DB level ondelete='CASCADE'
        order_by='Table.seat_number',
    )
Table has 1 Cafe
cafe: Mapped['Cafe'] = relationship(
    'Cafe',
    back_populates='tables',
    lazy='joined',
    # do not need cascade here!
)

"""
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import NAME_MIN_LENGTH, ADDRESS_MIN_LENGTH, \
    NAME_MAX_LENGTH, ADDRESS_MAX_LENGTH, PHONE_MAX_LENGTH
from app.models.base import TimestampedActiveModel, IntIDPKModel
from app.models.cafe_manager import cafe_managers
from app.models.dish_cafe import dish_cafes

if TYPE_CHECKING:
    from app.models import Booking, CafeManager, Dish, Slot, Table


class Cafe(TimestampedActiveModel, IntIDPKModel):
    """Модель кафе."""

    name: Mapped[str] = mapped_column(
        String(NAME_MAX_LENGTH),
        nullable=False,
        index=True,
        comment='Название',
    )
    address: Mapped[str] = mapped_column(
        String(ADDRESS_MAX_LENGTH),
        nullable=False,
        comment='Адрес',
    )
    phone: Mapped[str] = mapped_column(
        String(PHONE_MAX_LENGTH),
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
        ForeignKey('photo.id', ondelete="SET NULL"),
        nullable=True,
        comment='ID изображения',

    )
    dishes: Mapped[list['Dish']] = relationship(
        'Dish',
        secondary=dish_cafes,
    )
    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='cafe',
        cascade='save-update, merge, delete',
        passive_deletes=True,
        lazy='selectin',
        order_by='Booking.booking_date.desc()',
    )
    managers: Mapped[list['User']] = relationship(
        'User',
        secondary=cafe_managers
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge, delete',
        passive_deletes=True,
        order_by='Slot.start_time',
    )
    tables: Mapped[list['Table']] = relationship(
        'Table',
        back_populates='cafe',
        lazy='selectin',
        cascade='save-update, merge, delete',
        passive_deletes=True,
        order_by='Table.seat_number',
    )

    __table_args__ = (
        CheckConstraint((func.char_length(name) > NAME_MIN_LENGTH),name="ck_cafe_name_min_length"),
        CheckConstraint((func.char_length(address) > ADDRESS_MIN_LENGTH), name="ck_cafe_address_min_length"),
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
