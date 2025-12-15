from sqlalchemy import Column, ForeignKey, Table

from app.core.db import Base

cafe_managers = Table(
    'cafe_managers',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True),
)
