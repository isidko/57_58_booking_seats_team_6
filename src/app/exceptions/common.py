from http import HTTPStatus
from typing import ClassVar


class AppError(Exception):
    """Базовое исключение с HTTP-статусом и сообщением.

    https://fastapi.tiangolo.com/ru/tutorial/handling-errors/
    """

    status_code: ClassVar[HTTPStatus]

    def __init__(
        self,
        message: str,
    ) -> None:
        """Сохранить сообщение и статус, пробросить в базовый Exception."""
        self.message = message
        super().__init__(message)


class ObjectDoesNotExist(AppError):
    """Исключение для случая, когда объект не найден."""

    status_code = HTTPStatus.NOT_FOUND


class ObjectIsNotActive(AppError):
    """Исключение для случая, когда объект неактивен."""

    status_code = HTTPStatus.LOCKED


class ObjectDoesNotBelongToAnotherObject(AppError):
    """Исключение для случая, когда объект не принадлежит другому объекту."""

    status_code = HTTPStatus.NOT_FOUND


class CommonDBValidationError(AppError):
    """Общее исключение для ошибок валидации БД."""

    status_code = HTTPStatus.CONFLICT
