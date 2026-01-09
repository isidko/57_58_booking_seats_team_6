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
    auth_router,
    prefix='/auth',
    tags=['Аутентификация'],
)
main_router.include_router(
    users_router,
    prefix='/users',
    tags=['Пользователи'],
)
main_router.include_router(
    cafes_router,
    prefix='/cafe',
    tags=['Кафе'],
)
main_router.include_router(
    table_router,
    prefix='/table',
    tags=['Столы'],
)
main_router.include_router(
    slot_router,
    prefix='/slot',
    tags=['Временные слоты'],
)
main_router.include_router(
    booking_router,
    prefix='/booking',
    tags=['Бронирования'],
)
main_router.include_router(
    photo_router,
    prefix='/photo',
    tags=['Медиа'],
)
