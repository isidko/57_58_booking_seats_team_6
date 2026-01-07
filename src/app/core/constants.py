from enum import StrEnum

# Общие ограничения для названий и адресов
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 200
ADDRESS_MIN_LENGTH = 5
ADDRESS_MAX_LENGTH = 256

# Ограничения для фото
ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
PHOTO_PATH_MAX_LENGTH = 1024
UPLOAD_DIR = 'media'

# Ограничения для кафе
MAX_MANAGERS = 10
CAFE_MIN_SEAT_NUMBER = 1
CAFE_MAX_SEAT_NUMBER = 20
SLOT_MIN_DURATION_MINUTES = 30
DESCRIPTION_MIN_LENGTH = 5
DESCRIPTION_MAX_LENGTH = 200
NOTE_MAX_LENGTH=20000
GUEST_NUMBER_MIN = 1
GUEST_NUMBER_MAX = 10

# Ограничения для телефонов
PHONE_MIN_LENGTH = 12
PHONE_MAX_LENGTH = 32

# Ограничения для блюд
DISH_NAME_MIN_LENGTH = 2
DISH_NAME_MAX_LENGTH = 64

# Ограничения для пользователей
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
EMAIL_MIN_LENGTH = 5
EMAIL_MAX_LENGTH = 100
TG_ID_MIN_LENGTH = 1
TG_ID_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_HASH_MAX_LENGTH = 255
PASSWORD_HASH_MIN_LENGTH = 4

DEFAULT_QUERY_LIMIT = 100
MAX_QUERY_LIMIT = 1000

# Для логгирования
SYSTEM_USERNAME = 'SYSTEM'


class Scopes(StrEnum):
    """Перечень прав для разграничения доступа в API."""

    USERS_READ = 'users:read'
    USERS_WRITE = 'users:write'
    USERS_UPDATE = 'users:update'
    USERS_ME = 'users:me'

    CAFES_READ = 'cafes:read'
    CAFES_WRITE = 'cafes:write'
    CAFES_UPDATE = 'cafes:update'

    TABLES_READ = 'tables:read'
    TABLES_WRITE = 'tables:write'
    TABLES_UPDATE = 'tables:update'

    TIME_SLOTS_READ = 'time_slots:read'
    TIME_SLOTS_WRITE = 'time_slots:write'
    TIME_SLOTS_UPDATE = 'time_slots:update'

    DISHES_READ = 'dishes:read'
    DISHES_WRITE = 'dishes:write'
    DISHES_UPDATE = 'dishes:update'

    BOOKING_READ = 'booking:read'
    BOOKING_WRITE = 'booking:write'
    BOOKING_UPDATE = 'booking:update'

    MEDIA_READ = 'media:read'
    MEDIA_WRITE = 'media:write'


ADMIN_PERMISSIONS = [scope.value for scope in Scopes]

USER_PERMISSIONS = [
    Scopes.USERS_ME.value,
    Scopes.USERS_UPDATE.value,
    Scopes.CAFES_READ.value,
    Scopes.TABLES_READ.value,
    Scopes.TIME_SLOTS_READ.value,
    Scopes.DISHES_READ.value,
    Scopes.MEDIA_READ.value,
    Scopes.BOOKING_READ.value,
    Scopes.BOOKING_WRITE.value,
    Scopes.BOOKING_UPDATE.value,
]

MANAGER_PERMISSIONS = list({
    Scopes.USERS_READ.value,
    Scopes.USERS_UPDATE.value,
    Scopes.CAFES_UPDATE.value,
    Scopes.TABLES_UPDATE.value,
    Scopes.TIME_SLOTS_WRITE.value,
    Scopes.TIME_SLOTS_UPDATE.value,
    Scopes.DISHES_WRITE.value,
    Scopes.DISHES_UPDATE.value,
    Scopes.MEDIA_WRITE.value,
    *USER_PERMISSIONS,
})
