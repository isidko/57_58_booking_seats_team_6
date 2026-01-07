from enum import StrEnum


# Вероятно стоит перенести в constants
class ErrorMessages(StrEnum):
    """Сообщения об ошибках для API."""

    # Общие ошибки
    INVALID_UUID = 'Неверный формат UUID'
    NOT_ENOUGH_PERMISSIONS = 'Недостаточно прав'
    INACTIVE_USER = 'Пользователь неактивен'
    INTERNAL_SERVER_ERROR = 'Внутренняя ошибка сервера'
    DATABASE_ERROR = 'Ошибка базы данных'

    # Ошибки файлов
    FILE_NOT_FOUND = 'Файл не найден'
    FILE_READ_ERROR = 'Ошибка при чтении файла'
    FILE_WRITE_ERROR = 'Ошибка при сохранении файла'
    FILE_WRITE_UNEXPECTED_ERROR = 'Неожиданная ошибка при сохранении файла'
    FILE_PERMISSION_DENIED = 'Нет доступа к файлу'
    FILE_TOO_LARGE = 'Размер файла превышает 5 МБ'
    UNSUPPORTED_FILE_FORMAT = (
        'Неподдерживаемый формат файла. Разрешены: {allowed_formats}'
    )
    UNREADABLE_IMAGE = 'Невозможно распознать изображение'
    IMAGE_PROCESSING_ERROR = 'Ошибка при обработке изображения'

    # Ошибки фото
    PHOTO_NOT_FOUND = 'Изображение не найдено'
    PHOTO_NOT_FOUND_IN_DB = 'Изображение не найдено в базе данных'
    PHOTO_NOT_FOUND_ON_DISK = 'Файл изображения не найден на диске'

    # Ошибки загрузки
    UPLOAD_PERMISSION_DENIED = 'Нет прав для загрузки файлов'

    @classmethod
    def unsupported_format(cls, allowed_formats: str) -> str:
        """Форматированное сообщение о неподдерживаемом формате."""
        return cls.UNSUPPORTED_FILE_FORMAT.value.format(
            allowed_formats=allowed_formats,
        )
