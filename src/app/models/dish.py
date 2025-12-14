from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import TimestampedActiveIntIDModel

if TYPE_CHECKING:
    from app.models import Cafe


class Dish(TimestampedActiveIntIDModel):
    """Модель блюда."""

    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment='Название',
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
        index=True,
        comment='ID изображения',
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),  # 10 цифр, 2 после запятой
        nullable=False,
        comment='Цена',
    )
    cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary='dishcafes',
        back_populates='dishes',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint('price > 0', name='check_positive_price'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.name=}, '
            f'{self.price=}.'
        )
