"""
dish_cafes - M2M table between Dish table and a Cafe table.

In this M2M table we are using the composite primary key - by dish_id and cafe_id.
Ref to docs: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many
We do not need an unique constraint as the composite key will restrict it itself.
(1,2) and (1,2) as a PK is RESTRICTED!
"""

from sqlalchemy import ForeignKey, Column, Table

from app.core.db import Base

dish_cafes = Table(
    'dish_cafes',
    Base.metadata,
    Column('dish_id', ForeignKey('dishes.id', ondelete='CASCADE'), primary_key=True),
    Column('cafe_id', ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
)
