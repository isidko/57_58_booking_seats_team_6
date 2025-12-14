import uuid
from datetime import datetime

from app.core.db import Base
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampedActiveModel(Base):
    """Абстрактная базовая модель с общими полями."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment='Дата и время создания записи',
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment='Дата и время последнего обновления записи',
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default='true',
        nullable=False,
        index=True,
        comment='Флаг активности записи',
    )

    def activate(self) -> None:
        """Активировать запись."""
        self.is_active = True

    def deactivate(self) -> None:
        """Деактивировать запись."""
        self.is_active = False


class TimestampedActiveIntIDModel(TimestampedActiveModel):
    """Абстрактная модель с Integer ID."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='Уникальный идентификатор (Integer)',
    )


class TimestampedActiveUUIDModel(TimestampedActiveModel):
    """Абстрактная модель с UUID ID."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment='Уникальный идентификатор (UUID)',
    )
