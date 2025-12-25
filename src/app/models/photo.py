from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import PHOTO_PATH_MAX_LENGTH
from app.models.base import TimestampedActiveModel, UUIDPKModel


class Photo(TimestampedActiveModel, UUIDPKModel):
    """Модель фото."""

    location: Mapped[str] = mapped_column(
        String(PHOTO_PATH_MAX_LENGTH),
        nullable=False,
        unique=True,
        comment='Относительный путь к изображению',
    )

    def __repr__(self) -> str:
        return f'{self.id=}, {self.location=}.'
