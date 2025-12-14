from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TimestampedActiveIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe, Dish


class DishCafe(TimestampedActiveIntIDModel):
    """Промежуточная модель для связи блюдо-кафе."""

    dish_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('dishes.id'),
        primary_key=True,
    )
    cafe_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cafes.id'),
        primary_key=True,
    )
    dish: Mapped['Dish'] = relationship(
        'Dish',
        back_populates='cafes',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='dishes',
    )

    __table_args__ = (
        UniqueConstraint('dish_id', 'cafe_id', name='uq_dish_cafe'),
    )
