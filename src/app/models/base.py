import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AbstractBaseModel(Base):
    """Абстрактная базовая модель с общими полями"""

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

    def __repr__(self):
        return (
            f'{self.created_at=}, '
            f'{self.updated_at=}, '
            f'{self.is_active=}.'
        )


class AbstractIntIDModel(AbstractBaseModel):
    """Абстрактная модель с Integer ID"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment='Уникальный идентификатор (Integer)'
    )

    def __repr__(self):
        return (
            f'{self.id=}, '
            f'{super().__repr__()}'
        )


class AbstractUUIDModel(AbstractBaseModel):
    """Абстрактная модель с UUID ID"""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment='Уникальный идентификатор (UUID)'
    )

    def __repr__(self):
        return (
            f'{self.id=}, '
            f'{super().__repr__()}'
        )
