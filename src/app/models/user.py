from app.core.db import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя."""
