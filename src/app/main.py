from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.exceptions.common import AppError


@app.exception_handler(AppError)  # noqa: F821
async def app_error_handler(
        request: Request,
        exc: AppError,
) -> JSONResponse:
    """Обработчик исключений приложения.

    https://fastapi.tiangolo.com/ru/tutorial/handling-errors/

    Args:
        request: HTTP запрос.
        exc: Исключение приложения.

    Returns:
        JSONResponse

    """
    logger.opt(exception=exc).error(
        "{method} {url}\n{type}: {code} - {msg}",
        method=request.method,
        url=request.url,
        type=exc.__class__.__name__,
        code=exc.status_code,
        msg=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.__class__.__name__},
    )
