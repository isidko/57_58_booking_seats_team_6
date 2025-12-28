from http import HTTPStatus

from app.exceptions.common import AppError


class ForbiddenError(AppError):
    """Ошибка доступа - операция запрещена."""

    status_code = HTTPStatus.FORBIDDEN


class AuthError(AppError):
    """Ошибка аутентификации."""

    status_code = HTTPStatus.UNAUTHORIZED
