from fastapi import APIRouter

from app.api.endpoints import (
    auth_router,
    booking_router,
    cafes_router,
    photo_router,
    slot_router,
    table_router,
    users_router,
)

main_router = APIRouter()
main_router.include_router(
    auth_router, prefix='/auth', tags=['auth'],
)
main_router.include_router(
    booking_router,
    prefix='/booking',
    tags=['booking'],
)
main_router.include_router(
    cafes_router,
    prefix='/cafe',
    tags=['cafe'],
)
main_router.include_router(
    slot_router,
    prefix='/slot',
    tags=['slot'],
)

main_router.include_router(
    table_router,
    prefix='/table',
    tags=['table'],
)

main_router.include_router(
    photo_router,
    prefix='/photo',
    tags=['photo'],
)
main_router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)
