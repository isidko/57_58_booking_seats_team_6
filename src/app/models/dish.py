from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DISH_NAME_MAX_LENGTH
from app.models.base import IntIDPKModel, TimestampedActiveModel
from app.models.dish_cafe import dish_cafes

if TYPE_CHECKING:
    from app.models import Cafe


class Dish(TimestampedActiveModel, IntIDPKModel):
    """Модель блюда.

    We are not sure about the plural default naming, that is why
    we need to overwrite the __tablename__ with "dishes"
    """

    __tablename__ = "dishes"

    name: Mapped[str] = mapped_column(
        String(DISH_NAME_MAX_LENGTH),
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
        ForeignKey('photo.id', ondelete="SET NULL"),
        nullable=True,
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
        secondary=dish_cafes,
    )

    __table_args__ = (
        CheckConstraint((price > 0), name='check_positive_price'),
    )

    def __repr__(self) -> str:
        return (
            f'{self.name=}, '
            f'{self.price=}.'
        )
