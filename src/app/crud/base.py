from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load

from app.core.constants import DEFAULT_QUERY_LIMIT, MAX_QUERY_LIMIT
from app.core.db import Base

# -----------------------------------------------------------------------------
# Generic Type Variables для параметризации класса CRUDBase
# -----------------------------------------------------------------------------
# ModelType: любой класс SQLAlchemy модели, унаследованный от Base
# CreateSchemaType: Pydantic схема для создания (валидация входных данных)
# UpdateSchemaType: Pydantic схема для обновления (частичное обновление)
ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD операций.

    Использует Generics для типобезопасной работы с различными моделями
    и схемами. Наследуйте этот класс для конкретных моделей:

    Пример:
        class TableCRUD(CRUDBase[Table, TableCreate, TableUpdate]):
            pass

        table_crud = TableCRUD(Table)

    Параметры Generic:
        ModelType: SQLAlchemy модель (наследник Base)
        CreateSchemaType: Pydantic схема для создания записи
        UpdateSchemaType: Pydantic схема для обновления записи
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUDBase с конкретной моделью.

        Args:
            model: Класс SQLAlchemy модели, с которой будут работать
                   CRUD операции. Должен быть наследником Base.

        """
        self.model = model

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
        **extra_fields: Any,
    ) -> ModelType:
        """Создает новый запись в базе данных.

        Args:
            session: Асинхронная сессия SQLAlchemy
            obj_in: Валидированные данные для создания записи (Pydantic схема)
            **extra_fields: Дополнительные поля, которые нужно добавить к
                            записи (например, хэш пароля, временные метки)

        Returns:
            Созданный объект модели с заполненными полями
            (включая сгенерированный ID)

        Example:
            user = await user_crud.create(
                session,
                user_create_schema,
                hashed_password=hash_password(password)
            )

        """
        # Конвертируем Pydantic схему в словарь и добавляем дополнительные поля
        obj_in_data = obj_in.model_dump()
        obj_in_data.update(extra_fields)

        # Создаем экземпляр SQLAlchemy модели
        db_obj = self.model(**obj_in_data)

        # Сохраняем в базе данных
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        # Возвращаем созданный объект
        return db_obj

    async def get_by_pk(
        self,
        session: AsyncSession,
        pk: Any,
    ) -> ModelType | None:
        """Получает запись из базы данных по первичному ключу.

        Args:
            session: Асинхронная сессия SQLAlchemy
            pk: Значение первичного ключа.

        Returns:
            Объект модели или None, если запись не найдена.

        """
        # Выполняем запрос и возвращаем результаты
        return await session.get(self.model, pk)

    async def get_multi(
        self,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        active_objects_only: bool = True,
        where_expr: ColumnElement[bool] = true(),
        options: Sequence[Load] = (),
    ) -> list[ModelType]:
        """Получает несколько записей из базы данных.

        Поддерживает фильтрацию, пагинацию (limit/offset) и eager loading.

        Args:
            session: Асинхронная сессия SQLAlchemy
            limit: Максимальное количество записей.
                   None - использовать DEFAULT_QUERY_LIMIT
                   >0 - использовать указанный лимит
                        (ограничено MAX_QUERY_LIMIT)
            offset: Количество записей, которые нужно пропустить.
                    Используется для пагинации (по умолчанию 0).
            active_objects_only: Если True и модель имеет поле is_active,
                                 фильтрует только активные записи
            where_expr: SQLAlchemy выражение для дополнительной фильтрации.
                        Может содержать сложные условия
                        (AND, OR, LIKE, сравнения и т.д.)
            options: Последовательность SQLAlchemy ORM опций.
                     Позволяет избежать N+1 проблемы и оптимизировать запросы.
                     Пример: [selectinload(Cafe.tables)]

        Returns:
            Последовательность объектов модели

        Raises:
            ValueError: Если limit <= 0 или offset < 0

        """
        # Базовый запрос SELECT
        query = select(self.model)

        # Применяем ORM опции
        query = query.options(*options)

        # Фильтр по активности
        if active_objects_only:
            # Проверяем, что модель имеет поле is_active
            is_active_attr = getattr(self.model, 'is_active', None)
            if is_active_attr is not None:
                query = query.where(is_active_attr)

        # Применяем пользовательские условия фильтрации
        query = query.where(where_expr)

        # Валидация offset
        if offset < 0:
            raise ValueError(
                'Значение offset не может быть отрицательным. '
                f'Получено: {offset}',
            )

        # Применяем offset (пропуск записей) для пагинации
        query = query.offset(offset)

        # Обработка лимита
        if limit is None:
            # Используем лимит по умолчанию
            limit = DEFAULT_QUERY_LIMIT
        elif limit <= 0:
            raise ValueError(
                f'Значение limit должно быть положительным. Получено: {limit}',
            )
        else:
            # Применяем максимальное ограничение
            limit = min(limit, MAX_QUERY_LIMIT)

        # Применяем лимит к запросу
        query = query.limit(limit)

        # Выполняем запрос и возвращаем результаты
        return list((await session.execute(query)).scalars().all())

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Обновляет существующую запись в базе данных.

        Использует частичное обновление (PATCH) - обновляются только переданные
        поля. Поддерживает очистку nullable полей через None.

        Args:
            session: Асинхронная сессия SQLAlchemy
            db_obj: Существующий объект модели для обновления
            obj_in: Данные для обновления (Pydantic схема).

        Returns:
            Обновленный объект модели

        """
        # Получаем все явно переданные поля
        # exclude_unset=True: исключаем поля, которые вообще не передавались
        # exclude_none=False: сохраняем явно переданные None
        #                     (для очистки nullable полей)
        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude_none=False,
        )

        # Если нет данных для обновления, возвращаем исходный объект
        if not update_data:
            return db_obj

        # Обновляем поля объекта
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        # Сохраняем изменения в базе данных
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        # Возвращаем обновленный объект
        return db_obj
