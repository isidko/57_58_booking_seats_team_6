from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TimestampedActiveIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe, User


class CafeManager(TimestampedActiveIntIDModel):
    """Промежуточная модель для связи кафе-пользователь."""

    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        primary_key=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='cafe_managers',
    )
    manager: Mapped['User'] = relationship(
        'User',
        back_populates='cafe_managers',
    )

    __table_args__ = (
        UniqueConstraint('cafe_id', 'user_id', name='uq_cafe_manager'),
    )
