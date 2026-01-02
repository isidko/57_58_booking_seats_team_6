from fastapi import APIRouter

from app.api.endpoints import security_router

main_router = APIRouter()
main_router.include_router(
    security_router, prefix='/auth', tags=['auth'],
)
