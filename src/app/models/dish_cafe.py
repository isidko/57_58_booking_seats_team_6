from sqlalchemy import Column, ForeignKey, Table

from app.core.db import Base

dish_cafes = Table(
    'dish_cafes',
    Base.metadata,
    Column(
        'dish_id',
        ForeignKey('dishes.id', ondelete='RESTRICT'),
        primary_key=True,
    ),
    Column(
        'cafe_id',
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        primary_key=True,
    ),
)
