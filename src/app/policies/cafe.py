"""Policy-слой для Cafe.

Задачи модуля:
- Преобразовать (current_user, show_all, obj_in) в "контекст доступа" для CRUD:
  - active_objects_only: bool — нужно ли фильтровать только активные записи.
  - where_expr: SQLAlchemy expression — дополнительный фильтр.
- Выполнять RBAC/ABAC-проверки и бросать HTTPException при запрете.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import ColumnElement, or_, select, true

from app.exceptions.api import ForbiddenError
from app.models.cafe import Cafe
from app.models.cafe_manager import cafe_managers
from app.models.user import User, UserRole
from app.schemas.cafe import CafeUpdate


@dataclass(frozen=True)
class CafeReadContext:
    """Контекст чтения кафе для передачи в CRUD.

    active_objects_only:
        True  -> CRUD должен вернуть только активные записи (isactive=True).
        False -> CRUD может вернуть и активные, и неактивные записи.
    where_expr:
        Дополнительное SQL-условие доступа (например, manager-scope).
    """

    active_objects_only: bool
    where_expr: ColumnElement[bool]


class CafePolicy:
    """Policy для Cafe: строит SQL-фильтры доступа на чтение.

    Правила:
    - USER: видит только активные кафе (show_all игнорируется).
    - MANAGER:
        - show_all=False: видит только свои активные.
        - show_all=True: видит все активные + свои неактивные.
    - ADMIN:
        - show_all=False: видит все активные.
        - show_all=True: видит все активные + неактивные.
    """

    def _manager_scope_expr(self, user_id: int) -> ColumnElement[bool]:
        """SQL-выражение "кафе, которыми управляет менеджер".

        Возвращает условие вида:
            Cafe.id IN (SELECT cafe_id FROM cafe_managers
            WHERE user_id=:manager_id)
        """
        return Cafe.id.in_(
            select(cafe_managers.c.cafe_id).where(cafe_managers.c.user_id == user_id),
        )

    def read_context(
        self,
        current_user: User,
        show_all: bool,
    ) -> CafeReadContext:
        """Сформировать правила доступа для чтения Cafe.

        Правила:
        - USER: show_all запрещён; видит только активные кафе.
        - ADMIN: при show_all=True видит и неактивные, иначе только активные.
        - MANAGER:
            - show_all=False: видит все активные кафе (не только свои).
            - show_all=True: видит все активные + неактивные только своих кафе.
        """
        if current_user.role == UserRole.ADMIN:
            return CafeReadContext(
                active_objects_only=not show_all,
                where_expr=true(),
            )

        if current_user.role == UserRole.MANAGER:
            scope = self._manager_scope_expr(current_user.id)

            if show_all:
                return CafeReadContext(
                    active_objects_only=False,
                    where_expr=or_(Cafe.is_active.is_(True), scope),
                )

            return CafeReadContext(
                active_objects_only=True,
                where_expr=true(),
            )

        # USER (и прочие “обычные” роли) — только активные
        return CafeReadContext(active_objects_only=True, where_expr=true())

    def update_where_expr(self, current_user: User) -> ColumnElement[bool]:
        """Фильтр для update: менеджер может обновлять только свои кафе."""
        if current_user.role == UserRole.MANAGER:
            return self._manager_scope_expr(current_user.id)
        return true()

    def assert_update_payload_allowed(
        self,
        current_user: User,
        obj_in: CafeUpdate,
    ) -> None:
        """Проверяем, что пользователь имеет право присылать такие поля."""
        if current_user.role == UserRole.MANAGER:
            if obj_in.managers_id is not None:
                raise ForbiddenError('MANAGER cannot change managers_id')
            if obj_in.is_active is not None:
                raise ForbiddenError('MANAGER cannot change is_active')

        if obj_in.is_active is not None and (current_user.role != UserRole.ADMIN):
            raise ForbiddenError('Only ADMIN can change is_active')
