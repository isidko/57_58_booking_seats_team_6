from app.crud.base import CRUDBase
from app.models import Table
from app.schemas.table import TableCreate, TableUpdate


class TableCRUD(CRUDBase[Table, TableCreate, TableUpdate]):
    """CRUD операции для столов."""


table_crud = TableCRUD(Table)
