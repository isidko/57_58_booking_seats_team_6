from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from app.core.constants import (
    EMAIL_MAX_LENGTH,
    EMAIL_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_MIN_LENGTH,
    TG_ID_MAX_LENGTH,
    TG_ID_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from app.models.user import UserRole
from app.schemas.common import TimestampedActiveSchema


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    username: str = Field(
        ...,
        description='Имя пользователя',
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        examples=['user123'],
    )

    email: Optional[str] = Field(
        None,
        description='Email',
        min_length=EMAIL_MIN_LENGTH,
        max_length=EMAIL_MAX_LENGTH,
        examples=['user@example.com'],
    )

    phone: Optional[str] = Field(
        None,
        description='Телефон',
        min_length=PHONE_MIN_LENGTH,
        max_length=PHONE_MAX_LENGTH,
        examples=['+79876543210'],
    )

    tg_id: Optional[str] = Field(
        None,
        description='Telegram ID',
        min_length=TG_ID_MIN_LENGTH,
        max_length=TG_ID_MAX_LENGTH,
        examples=['123456789'],
    )


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str = Field(
        ...,
        description='Пароль',
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        examples=['securepassword123'],
    )

    @model_validator(mode='after')
    def validate_contacts(self) -> Self:
        """Проверяет, что указан email или телефон."""
        if not self.email and not self.phone:
            raise ValueError('Должен быть указан email или телефон')
        return self


class UserUpdate(UserBase):
    """Схема для обновления информации о пользователе."""

    username: Optional[str] = Field(
        None,
        description='Имя пользователя',
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        examples=['user123'],
    )

    password: Optional[str] = Field(
        None,
        description='Пароль',
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        examples=['new_securepassword123'],
    )

    role: Optional[UserRole] = Field(
        None,
        description='Роль пользователя (0 - USER, 1 - MANAGER, 2 - ADMIN)',
        # Используем .value для Swagger
        examples=[UserRole.USER.value],
    )

    is_active: Optional[bool] = Field(
        None,
        description='Флаг активности',
        examples=[True],
    )

    @model_validator(mode='after')
    def validate_empty_body(self) -> Self:
        """Проверяет, что тело запроса не пустое.

        Если пришёл PATCH-запрос с пустым телом ({}), выбрасывает ошибку.
        """
        if not self.model_fields_set:
            raise ValueError('Тело запроса не может быть пустым')
        return self

    @model_validator(mode='after')
    def validate_contacts(self) -> Self:
        """Проверяет наличие email или телефона при обновлении..

        Подробности:
        - Если в запросе обновления указаны оба поля (email и phone),
        то хотя бы одно из них должно быть непустым.
        """
        # Проверяем, что оба поля пришли в запросе
        if {'email', 'phone'}.issubset(self.model_fields_set):
            # Если оба поля пришли, то хотя бы одно должно быть не None
            if not self.email and not self.phone:
                raise ValueError(
                    'Хотя бы одно из полей (email или phone)'
                    'должно быть заполнено',
                )
        return self


class UserShortInfo(UserBase):
    """Краткая информация о пользователе.

    Наследует поля username, email, phone, tg_id от UserBase.
    """

    id: int = Field(
        ...,
        description='Уникальный идентификатор пользователя',
        examples=[1],
    )

    model_config = ConfigDict(from_attributes=True)


class UserInfo(UserShortInfo, TimestampedActiveSchema):
    """Полная информация о пользователе.

    Наследует id, username, email, phone, tg_id от UserShortInfo
    и created_at, updated_at, is_active от TimestampedActiveSchema.
    """

    role: UserRole = Field(
        ...,
        description='Роль пользователя (0 - USER, 1 - MANAGER, 2 - ADMIN)',
        # Используем .value для Swagger
        examples=[UserRole.USER.value],
    )

    # Добавлен конфиг для корректной работы с ORM-моделями
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Схема для аутентификации пользователя."""

    login: str = Field(
        ...,
        description='Логин пользователя (email или телефон)',
        examples=['user@example.com'],
    )

    password: str = Field(
        ...,
        description='Пароль пользователя',
        examples=['securepassword123'],
    )


class AuthToken(BaseModel):
    """Схема для токена аутентификации."""

    access_token: str = Field(
        ...,
        description='Токен доступа',
        examples=['eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'],
    )

    token_type: str = Field(
        ...,
        description='Тип токена',
        examples=['bearer'],
    )
