import io
import os
import uuid
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException, UploadFile, status

from app.core.constants import (
    ALLOWED_CONTENT_TYPES,
    SYSTEM_USERNAME,
    UPLOAD_DIR,
)
from app.core.error_messages import ErrorMessages
from app.core.log_level import LogLevel
from app.core.logging import log_message


class PhotoUtils:
    """Утилиты для работы с фотографиями."""

    @staticmethod
    async def validate_upload_file(
        file: UploadFile,
        username: str = SYSTEM_USERNAME,
    ) -> None:
        """Валидация загружаемого файла."""
        # Проверка типа содержимого
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            log_message(
                message=(
                    'Попытка загрузки файла с неподдерживаемым форматом: '
                    f'{file.content_type}'
                ),
                level=LogLevel.WARNING,
                username=username,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.unsupported_format(
                    allowed_formats=', '.join(ALLOWED_CONTENT_TYPES),
                ),
            )

    @staticmethod
    async def save_image_file(
        file: UploadFile,
        upload_dir: str = UPLOAD_DIR,
        username: str = SYSTEM_USERNAME,
        user_id: int | None = None,
    ) -> tuple[str, str]:
        """Сохранение загруженного файла и конвертация в JPG."""
        # Создание директории если не существует
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)

        # Генерация уникального имени файла
        filename = f'{uuid.uuid4()}.jpg'
        file_path = upload_path / filename

        try:
            # Чтение файла
            contents = await file.read()
            log_message(
                message=f'Загружен файл размером {len(contents)} байт',
                level=LogLevel.DEBUG,
                username=username,
                user_id=user_id,
            )

            # Открытие и конвертация изображения
            try:
                image = Image.open(io.BytesIO(contents))
                log_message(
                    message=(
                        f'Изображение открыто: формат={image.format}, '
                        f'размер={image.size}, режим={image.mode}'
                    ),
                    level=LogLevel.DEBUG,
                    username=username,
                    user_id=user_id,
                )
            except UnidentifiedImageError:
                log_message(
                    message=ErrorMessages.UNREADABLE_IMAGE,
                    level=LogLevel.WARNING,
                    username=username,
                    user_id=user_id,
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorMessages.UNREADABLE_IMAGE,
                )

            # Сохранение в формате JPG
            image.save(file_path, 'JPEG', quality=95, optimize=True)
            log_message(
                message=f'Файл сохранен: {file_path}',
                level=LogLevel.INFO,
                username=username,
                user_id=user_id,
            )

            return filename, str(file_path)

        except HTTPException:
            raise

        except OSError as e:
            # Ошибки файловой системы
            log_message(
                message=f'{ErrorMessages.FILE_WRITE_ERROR} {file_path}: {e}',
                level=LogLevel.ERROR,
                username=username,
                user_id=user_id,
            )
            if file_path.exists():
                file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorMessages.FILE_WRITE_ERROR,
            )

        except (Image.DecompressionBombError, ValueError) as e:
            # Ошибки PIL
            log_message(
                message=f'{ErrorMessages.IMAGE_PROCESSING_ERROR}: {e}',
                level=LogLevel.WARNING,
                username=username,
                user_id=user_id,
            )
            if file_path.exists():
                file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.IMAGE_PROCESSING_ERROR,
            )

        except Exception as e:
            # Удаляем файл если что-то пошло не так
            log_message(
                message=(
                    f'{ErrorMessages.FILE_WRITE_UNEXPECTED_ERROR} '
                    f'{type(e).__name__}: {e}'
                ),
                level=LogLevel.CRITICAL,
                username=username,
                user_id=user_id,
            )
            if file_path.exists():
                file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorMessages.FILE_WRITE_UNEXPECTED_ERROR,
            )

    @staticmethod
    def get_file_path(filename: str, upload_dir: str = UPLOAD_DIR) -> str:
        """Получение полного пути к файлу."""
        return os.path.join(upload_dir, filename)

    @staticmethod
    def read_file(
        file_path: str,
        username: str = SYSTEM_USERNAME,
        user_id: int | None = None,
    ) -> bytes:
        """Чтение файла в бинарном формате."""
        if not os.path.exists(file_path):
            log_message(
                message=f'{ErrorMessages.FILE_NOT_FOUND}: {file_path}',
                level=LogLevel.WARNING,
                username=username,
                user_id=user_id,
            )
            raise FileNotFoundError(
                f'{ErrorMessages.FILE_NOT_FOUND}: {file_path}',
            )

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                log_message(
                    message=f'Прочитано {len(content)} байт из {file_path}',
                    level=LogLevel.DEBUG,
                    username=username,
                    user_id=user_id,
                )
                return content
        except PermissionError as e:
            log_message(
                message=(
                    f'{ErrorMessages.FILE_PERMISSION_DENIED} {file_path}: {e}'
                ),
                level=LogLevel.ERROR,
                username=username,
                user_id=user_id,
            )
            raise PermissionError(
                f'{ErrorMessages.FILE_PERMISSION_DENIED}: {file_path}',
            )
        except OSError as e:
            log_message(
                message=f'{ErrorMessages.FILE_READ_ERROR} {file_path}: {e}',
                level=LogLevel.ERROR,
                username=username,
                user_id=user_id,
            )
            raise OSError(
                f'{ErrorMessages.FILE_READ_ERROR} {file_path}: {str(e)}',
            )


# Создаем инстанс для использования
photo_utils = PhotoUtils()
