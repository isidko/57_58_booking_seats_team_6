from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import ModelType
from app.models import User
from app.models.user import UserRole


async def get_owned_by_pk(
    model: type[ModelType],
    session: AsyncSession,
    object_pk: Any,
    user_instance: User,
) -> ModelType:
    """Check if this user owner of this object and return object if so.

    If it is admin or manager, return an object.
    If it is a User, check owner and return and object.
    """
    obj = await session.get(model, object_pk)
    if obj is None:
        raise HTTPException(404, "Not found")
    if user_instance.role in (UserRole.MANAGER, UserRole.ADMIN):
        return obj
    if obj.user_id != user_instance.id:
        raise HTTPException(403, "Not enough permissions")
    return obj
