from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship

from app.core.db import Base
from app.models.cafe_manager import cafe_managers

if TYPE_CHECKING:
    from app.models import Booking


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя."""

    __tablename__ = "users"

    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='user',
        cascade='save-update, merge, delete',
        passive_deletes=True,
        lazy='selectin',
        order_by='Booking.booking_date.desc()',
    )
    managed_cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary=cafe_managers,
    )
