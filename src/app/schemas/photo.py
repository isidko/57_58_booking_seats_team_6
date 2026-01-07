from pydantic import BaseModel, ConfigDict


class PhotoCreate(BaseModel):
    """Загрузка изображения."""

    location: str

    model_config = ConfigDict(from_attributes=True)


class PhotoInfo(BaseModel):
    """Информации о фото."""

    media_id: str

    model_config = ConfigDict(from_attributes=True)
