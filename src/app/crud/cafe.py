"""CRUD-слой для Cafe."""

from __future__ import annotations

from typing import Any, Sequence

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, delete, insert, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load

from app.crud.base import CRUDBase
from app.models.cafe import Cafe
from app.models.cafe_manager import cafe_managers
from app.schemas.cafe import CafeCreate, CafeUpdate


class CRUDCafe(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """CRUD для Cafe.

    Методы чтения принимают фильтры доступа, чтобы можно было:
    - вернуть только активные,
    - добавить ограничения по manager-scope,
    - переиспользовать CRUD без HTTP-контекста.
    """

    async def get(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        active_objects_only: bool = True,
        where_expr: ColumnElement[bool] = true(),
        options: Sequence[Load] = (),
    ) -> Cafe:
        """Получить Cafe по первичному ключу.

        Параметры:
        - active_objects_only: если True — ограничивает выборку активными
         (через CRUDBase.get_multi).
        - where_expr: дополнительный фильтр доступа (например, manager-scope).
        - options: SQLAlchemy options для eager-loading.

        Возвращает:
        - Cafe

        Исключения:
        - 404, если запись не найдена или отфильтрована условиями доступа.
        """
        cafes = await super().get_multi(
            session,
            limit=1,
            offset=0,
            active_objects_only=active_objects_only,
            where_expr=(where_expr & (Cafe.id == cafe_id)),
            options=options,
        )
        if not cafes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Cafe not found',
            )
        return cafes[0]

    async def set_managers(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        managers_id: list[int],
        check_existing: bool = True,
    ) -> None:
        """Обновить M2M-связь cafe_managers для указанного cafe_id.

        Если check_existing=True:
        - читается текущий набор менеджеров,
        - выполняется delta-update (delete + bulk insert).
        """
        new_ids = set(managers_id)

        if check_existing:
            res = await session.execute(
                select(cafe_managers.c.user_id).where(
                    cafe_managers.c.cafe_id == cafe_id,
                ),
            )
            old_ids = {row[0] for row in res.all()}
        else:
            old_ids = set()

        if old_ids == new_ids:
            return

        to_delete = old_ids - new_ids
        to_add = new_ids - old_ids

        if to_delete:
            await session.execute(
                delete(cafe_managers).where(
                    cafe_managers.c.cafe_id == cafe_id,
                    cafe_managers.c.user_id.in_(to_delete),
                ),
            )

        if to_add:
            await session.execute(
                insert(cafe_managers),
                [{'cafe_id': cafe_id, 'user_id': uid} for uid in to_add],
            )

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CafeCreate,
        managers_id: list[int],
    ) -> Cafe:
        """Создать Cafe и установить managers_id в связке cafe_managers."""
        data = obj_in.model_dump()
        data.pop('managers_id', None)

        cafe = Cafe(**data)
        session.add(cafe)
        await session.flush()

        await self.set_managers(
            session,
            cafe_id=cafe.id,
            managers_id=managers_id,
            check_existing=False,
        )

        await session.commit()
        await session.refresh(cafe)
        return cafe

    async def update(
        self,
        session: AsyncSession,
        *,
        cafe_id: int,
        data: dict[str, Any],
        managers_id: list[int] | None,
        active_objects_only: bool,
        where_expr: ColumnElement[bool],
    ) -> Cafe:
        """Обновить Cafe (PATCH) с учётом фильтров доступа.

        Параметры:
        - data: подготовленный policy словарь полей.
        - managers_id:
            None -> менеджеров не трогаем,
            list -> валидируем и обновляем M2M-связь.
        - active_objects_only / where_expr: применяются при чтении объекта
         перед обновлением.
        """
        cafe = await self.get(
            session,
            cafe_id=cafe_id,
            active_objects_only=active_objects_only,
            where_expr=where_expr,
        )

        for key, value in data.items():
            setattr(cafe, key, value)

        if managers_id is not None:
            await self.set_managers(
                session,
                cafe_id=cafe.id,
                managers_id=managers_id,
            )

        await session.commit()
        await session.refresh(cafe)
        return cafe


cafe_crud = CRUDCafe(Cafe)
