"""cafe_managers - M2M table between Cafe table and a User table.

In this M2M table we are using the composite primary key - by user_id and cafe_id.
Ref to docs: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
We do not need an unique constraint as the composite key will restrict it itself.
(1,2) and (1,2) as a PK is RESTRICTED!
"""

from sqlalchemy import Column, ForeignKey, Table

from app.core.db import Base

cafe_managers = Table(
    'cafe_managers',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True),
)
