from typing import Any, cast

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load, selectinload

from app.core.logging import LogLevel, log_message
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD операции для пользователей."""

    async def _check_unique_fields(
        self,
        session: AsyncSession,
        email: str | None = None,
        phone: str | None = None,
        exclude_user_id: int | None = None,
    ) -> None:
        """Проверяет уникальность email или телефона.

        Args:
            session: Асинхронная сессия SQLAlchemy.
            email: Email для проверки.
            phone: Телефон для проверки.
            exclude_user_id: ID пользователя, которого исключить из проверки.

        Raises:
            ValueError: Если email или телефон уже заняты.

        """
        conditions = []
        if email:
            conditions.append(User.email == email)
        if phone:
            conditions.append(User.phone == phone)

        if conditions:
            query = select(exists().where(or_(*conditions)))
            if exclude_user_id:
                query = query.where(User.id != exclude_user_id)
            if await session.scalar(query):
                raise ValueError('Email или телефон уже заняты.')

    async def create(
        self,
        session: AsyncSession,
        obj_in: UserCreate,
        **extra_fields: Any,
    ) -> User:
        """Создаёт нового пользователя с проверкой уникальности email/phone."""
        await self._check_unique_fields(
            session,
            email=obj_in.email,
            phone=obj_in.phone,
        )

        # Преобразуем UserCreate в словарь, исключая пароль
        obj_in_data = obj_in.model_dump(exclude={'password'})

        # Объединяем данные (extra_fields содержит password_hash из endpoint)
        create_data = {**obj_in_data, **extra_fields}

        # Создаем пользователя
        user = self.model(**create_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        log_message(
            f'Создан пользователь {user.id} ({user.username}).',
            LogLevel.INFO,
            user_id=user.id,
            username=user.username,
        )
        return user

    async def get_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> User | None:
        """Получает пользователя по имени пользователя."""
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """Получает пользователя по email."""
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_phone(
        self,
        session: AsyncSession,
        phone: str,
    ) -> User | None:
        """Получает пользователя по телефону."""
        query = select(User).where(User.phone == phone)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi_with_cafes(
        self,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        active_objects_only: bool = True,
    ) -> list[User]:
        """Получает список пользователей с подгруженными кафе."""
        options = cast(list[Load], [selectinload(User.managed_cafes)])
        return await super().get_multi(
            session=session,
            limit=limit,
            offset=offset,
            active_objects_only=active_objects_only,
            options=options,
        )

    async def update(
        self,
        session: AsyncSession,
        db_obj: User,
        obj_in: UserUpdate,
    ) -> User:
        """Обновляет пользователя с проверкой уникальности email/phone."""
        if obj_in.email or obj_in.phone:
            await self._check_unique_fields(
                session,
                email=obj_in.email,
                phone=obj_in.phone,
                exclude_user_id=db_obj.id,
            )
        user = await super().update(session, db_obj, obj_in)
        log_message(
            f'Обновлён пользователь {user.id} ({user.username}).',
            LogLevel.INFO,
            user_id=user.id,
            username=user.username,
        )
        return user

    async def block_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        """Блокирует пользователя."""
        user = await self.get_by_pk(session, user_id)
        if user is None:
            raise ValueError(f'Пользователь с ID {user_id} не найден.')
        user.is_active = False
        await session.commit()
        await session.refresh(user)  # Обновление состояния объекта
        log_message(
            f'Пользователь {user.id} ({user.username}) заблокирован.',
            LogLevel.WARNING,
            user_id=user.id,
            username=user.username,
        )
        return user

    async def unblock_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        """Разблокирует пользователя."""
        user = await self.get_by_pk(session, user_id)
        if user is None:
            raise ValueError(f'Пользователь с ID {user_id} не найден.')
        user.is_active = True
        await session.commit()
        await session.refresh(user)  # Обновление состояния объекта
        log_message(
            f'Пользователь {user.id} ({user.username}) разблокирован.',
            LogLevel.INFO,
            user_id=user.id,
            username=user.username,
        )
        return user


user_crud = UserCRUD(User)
