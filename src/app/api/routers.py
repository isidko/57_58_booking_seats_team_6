from fastapi import APIRouter

from app.api.endpoints import auth_router, booking_router, cafes_router

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
    prefix='/cafes',
    tags=['cafes'],
)
