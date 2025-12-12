from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import AbstractUUIDModel


class Photo(AbstractUUIDModel):
    location: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
        comment='Относительный путь к изображению'
    )

    def __repr__(self) -> str:
        return (
            f'{self.id=}, '
            f'{self.location=}, '
            f'{super().__repr__()}'
        )
