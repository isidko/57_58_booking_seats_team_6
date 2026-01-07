from app.crud.base import CRUDBase
from app.models import Photo
from app.schemas.photo import PhotoCreate


class PhotoCRUD(CRUDBase[Photo, PhotoCreate, None]):
    """CRUD операции для фотографий."""


photo_crud = PhotoCRUD(Photo)
