from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, String, column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    EMAIL_MAX_LENGTH,
    EMAIL_MIN_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    PASSWORD_HASH_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_MIN_LENGTH,
    TG_ID_MAX_LENGTH,
    TG_ID_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from app.models.base import IntIDPKModel, TimestampedActiveModel
from app.models.cafe_manager import cafe_managers

if TYPE_CHECKING:
    from app.models import Booking, Cafe


class UserRole(IntEnum):
    """Роли пользователей."""

    USER = 0
    MANAGER = 1
    ADMIN = 2


class User(TimestampedActiveModel, IntIDPKModel):
    """Модель пользователя."""

    __table_args__ = (
        # Проверяет, что или email, или username присутствует
        CheckConstraint(
            'email IS NOT NULL OR username IS NOT NULL',
            name='check_email_or_username_in_place',
        ),
    )

    # Имя пользователя: обязательное, уникальное, индексированное поле
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH),
        CheckConstraint(
            func.char_length(column('username')) >= USERNAME_MIN_LENGTH,
            name='username_min_length',
        ),
        nullable=False,
        unique=True,
        index=True,
        comment='Имя пользователя',
    )

    # Email: необязательное поле, может быть NULL
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_MAX_LENGTH),
        CheckConstraint(
            func.char_length(column('email')) >= EMAIL_MIN_LENGTH,
            name='email_min_length',
        ),
        nullable=True,  # Поле может быть NULL
        unique=True,
        index=True,
        comment='Email',
    )

    # Телефон: аналогично email, но с ограничением длины 20 символов
    phone: Mapped[str | None] = mapped_column(
        String(PHONE_MAX_LENGTH),
        CheckConstraint(
            func.char_length(column('phone')) >= PHONE_MIN_LENGTH,
            name='phone_min_length',
        ),
        nullable=True,
        unique=True,
        index=True,
        comment='Телефон',
    )

    # Telegram ID
    tg_id: Mapped[str | None] = mapped_column(
        String(TG_ID_MAX_LENGTH),
        CheckConstraint(
            func.char_length(column('tg_id')) >= TG_ID_MIN_LENGTH,
            name='tg_id_min_length',
        ),
        nullable=True,
        unique=True,
        index=True,
        comment='Telegram ID',
    )

    # Хеш пароля: обязательное поле, хранит хешированный пароль пользователя
    password_hash: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH),
        CheckConstraint(
            func.char_length(column('password_hash'))
            >= PASSWORD_HASH_MIN_LENGTH,
            name='password_hash_min_length',
        ),
        nullable=False,
        comment='Хеш пароля',
    )

    # Роль пользователя: целочисленное значение из UserRole
    role: Mapped[UserRole] = mapped_column(
        Integer,
        CheckConstraint(
            column('role').in_([
                UserRole.USER,
                UserRole.MANAGER,
                UserRole.ADMIN,
            ]),
            name='role_valid_values',
        ),
        nullable=False,
        default=UserRole.USER,
        index=True,
        comment='Роль пользователя',
    )

    bookings: Mapped[list['Booking']] = relationship(
        'Booking',
        back_populates='user',
        lazy='raise_on_sql',
    )

    managed_cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary=cafe_managers,
        back_populates='managers',
        lazy='raise_on_sql',
    )

    def __repr__(self) -> str:
        return f'{self.username=}, {self.role.name=}.'
