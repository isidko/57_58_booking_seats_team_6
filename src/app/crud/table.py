"""Предполагается наличие в cafe_crud следующих методов.

from sqlalchemy import exists, select
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import cafe_managers, Cafe
from app.schemas.cafe import CafeCreate, CafeUpdate


class CafeCRUD(CRUDBase[Cafe, CafeCreate, CafeUpdate]):

    def __init__(self):
        super().__init__(Cafe)

    async def get_cafe_with_manager_check(
        self,
        session: AsyncSession,
        cafe_id: int,
        user_id: int,
    ) -> Row[tuple[Cafe, bool]] | None:
        return (
            await session.execute(
                select(Cafe)
                .where(Cafe.id == cafe_id)
                .add_columns(
                    exists().where(
                        cafe_managers.c.cafe_id == cafe_id,
                        cafe_managers.c.user_id == user_id,
                    ).label('is_manager')
                )
            )
        ).first()

    async def get_cafe_with_tables_and_manager_check(
        self,
        session: AsyncSession,
        cafe_id: int,
        user_id: int,
    ) -> Row[tuple[Cafe, bool]] | None:
        return (
            await session.execute(
                select(Cafe)
                .where(Cafe.id == cafe_id)
                .add_columns(
                    exists().where(
                        cafe_managers.c.cafe_id == cafe_id,
                        cafe_managers.c.user_id == user_id,
                    ).label('is_manager')
                )
                .options(selectinload(Cafe.tables))
            )
        ).first()

cafe_crud = CafeCRUD()

"""

from sqlalchemy import exists, select
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Cafe, Table, cafe_managers
from app.schemas.table import TableCreate, TableUpdate


class TableCRUD(CRUDBase[Table, TableCreate, TableUpdate]):
    """CRUD операции для столов."""

    async def get_table_with_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        table_id: int,
        user_id: int,
    ) -> Row[tuple[Table, Cafe, bool]] | None:
        """Получить стол с информацией о кафе.

        Дополнительно проверяем, является ли пользователь менеджером кафе.
        """
        return (
            await session.execute(
                select(Table, Cafe)
                .join(Cafe, Table.cafe_id == Cafe.id)
                .where(
                    Table.id == table_id,
                    Table.cafe_id == cafe_id,
                )
                .add_columns(
                    exists().where(
                        cafe_managers.c.cafe_id == cafe_id,
                        cafe_managers.c.user_id == user_id,
                    ).label('is_manager'),
                ),
            )
        ).first()


table_crud = TableCRUD(Table)
