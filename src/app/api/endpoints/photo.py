import os
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Security,
    UploadFile,
    status,
)
from fastapi.responses import Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import get_current_user
from app.core.constants import Scopes
from app.core.db import get_async_session
from app.core.error_messages import ErrorMessages
from app.core.log_level import LogLevel
from app.core.logging import log_message
from app.core.utils import photo_utils
from app.crud.photo import photo_crud
from app.exceptions.database import DBObjectNotFoundError
from app.models.user import User
from app.schemas.photo import PhotoCreate, PhotoInfo

router = APIRouter()


@router.get(
    '/media/{media_id}',
    summary='Возвращает изображение в бинарном виде',
    response_class=Response,
)
async def get_photo(
    media_id: UUID = Path(..., description='UUID изображения'),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(
        get_current_user,
        scopes=[Scopes.MEDIA_READ.value],
    ),
) -> Response:
    """Получить фото по ID.

    Возвращает изображение в формате JPG в виде бинарных данных.
    """
    log_message(
        message=f'Запрос фото {media_id}',
        level=LogLevel.INFO,
        username=current_user.username,
        user_id=current_user.id,
    )

    # Получение записи из БД
    photo = await photo_crud.get_by_pk(session, media_id)
    if not photo:
        log_message(
            message=f'{ErrorMessages.PHOTO_NOT_FOUND_IN_DB}. ID: {media_id}',
            level=LogLevel.WARNING,
            username=current_user.username,
            user_id=current_user.id,
        )
        raise DBObjectNotFoundError(ErrorMessages.PHOTO_NOT_FOUND)

    # Проверка существования файла
    file_path = photo_utils.get_file_path(photo.location)
    if not os.path.exists(file_path):
        log_message(
            message=(
                f'Файл {photo.location} не найден на диске '
                f'для фото ID {media_id}'
            ),
            level=LogLevel.ERROR,
            username=current_user.username,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.PHOTO_NOT_FOUND_ON_DISK,
        )

    # Чтение и возврат файла
    try:
        file_content = photo_utils.read_file(
            file_path,
            username=current_user.username,
            user_id=current_user.id,
        )
        log_message(
            message=(
                f'Успешно отправлено фото {media_id} '
                f'({len(file_content)} байт)'
            ),
            level=LogLevel.INFO,
            username=current_user.username,
            user_id=current_user.id,
        )

        return Response(
            content=file_content,
            media_type='image/jpeg',
            headers={
                'Content-Disposition': 'inline',
                'Cache-Control': 'public, max-age=3600',
            },
        )

    except FileNotFoundError:
        # На случай если файл удалился между проверкой и чтением
        log_message(
            message=f'Файл {file_path} удален во время обработки запроса',
            level=LogLevel.ERROR,
            username=current_user.username,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.PHOTO_NOT_FOUND,
        )
    except PermissionError:
        log_message(
            message=f'{ErrorMessages.FILE_PERMISSION_DENIED} {file_path}',
            level=LogLevel.ERROR,
            username=current_user.username,
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.FILE_PERMISSION_DENIED,
        )
    except OSError as e:
        log_message(
            message=f'{ErrorMessages.FILE_READ_ERROR} {file_path}: {e}',
            level=LogLevel.ERROR,
            username=current_user.username,
            user_id=current_user.id,
        )
        # Ошибки ввода/вывода
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.FILE_READ_ERROR,
        )


@router.post(
    '/media',
    response_model=PhotoInfo,
    summary='Загрузка изображения',
    description=(
        'Загрузка изображения на сервер. Поддерживаются форматы jpg, png. '
        'Размер файла не более 5Мб. Только для администраторов и менеджеров'
    ),
)
async def upload_photo(
    file: UploadFile = File(
        ...,
        description='Изображение в формате JPG или PNG (макс. 5 МБ)',
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Security(
        get_current_user,
        scopes=[Scopes.MEDIA_WRITE.value],
    ),
) -> PhotoInfo:
    """Загрузить фото на сервер.

    Возвращает ID загруженного файла.
    """
    log_message(
        message='Начало загрузки фото',
        level=LogLevel.INFO,
        username=current_user.username,
        user_id=current_user.id,
    )

    # Валидация файла
    await photo_utils.validate_upload_file(
        file,
        username=current_user.username,
    )
    log_message(
        message=f'Файл {file.filename} прошел валидацию',
        level=LogLevel.DEBUG,
        username=current_user.username,
        user_id=current_user.id,
    )

    # Сохранение файла на диск
    filename, file_path = await photo_utils.save_image_file(
        file,
        username=current_user.username,
        user_id=current_user.id,
    )

    # Создание записи в БД
    try:
        photo = await photo_crud.create(
            session,
            PhotoCreate(location=filename),
        )
        log_message(
            message=f'Фото успешно загружено: ID={photo.id}, путь={filename}',
            level=LogLevel.INFO,
            username=current_user.username,
            user_id=current_user.id,
        )

        return PhotoInfo(media_id=str(photo.id))

    except SQLAlchemyError as e:
        # Ошибки БД при создании записи
        log_message(
            message=f'Ошибка БД при сохранении записи о фото {filename}: {e}',
            level=LogLevel.ERROR,
            username=current_user.username,
            user_id=current_user.id,
        )

        # Удаление файла
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                log_message(
                    message=f'Удален файл {file_path} из-за ошибки БД',
                    level=LogLevel.DEBUG,
                    username=current_user.username,
                    user_id=current_user.id,
                )
            except OSError as cleanup_error:
                log_message(
                    message=(
                        f'Не удалось удалить файл {file_path} '
                        f'после ошибки БД: {cleanup_error}'
                    ),
                    level=LogLevel.WARNING,
                    username=current_user.username,
                    user_id=current_user.id,
                )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка базы данных',
        )
