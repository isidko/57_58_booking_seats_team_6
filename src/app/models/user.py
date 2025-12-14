from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models import Booking, CafeManager


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя."""

    __tablename__ = "users"

    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='user',
        cascade='save-update, merge',
        lazy='selectin',
        order_by='Booking.booking_date.desc()',
    )
    cafe_managers: Mapped[list['CafeManager']] = relationship(
        'CafeManager',
        back_populates='manager',
        cascade='save-update, merge',
        lazy='selectin',
    )
