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
