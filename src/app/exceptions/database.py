from http import HTTPStatus

from app.exceptions.common import AppError


class DBError(AppError):
    """Общая ошибка базы данных."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class DBObjectNotFoundError(AppError):
    """Ошибка - объект не найден в базе данных."""

    status_code = HTTPStatus.NOT_FOUND


class DBConflictError(AppError):
    """Ошибка конфликта в базе данных."""

    status_code = HTTPStatus.CONFLICT
