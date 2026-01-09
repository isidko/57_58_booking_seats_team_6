# Booking Seats API

API для системы бронирования столов в кафе. Позволяет пользователям бронировать столы в кафе на определенные временные слоты, управлять бронированиями и получать уведомления по email.

## Основные возможности

- **Аутентификация и авторизация** - JWT-токены, роли пользователей (USER, MANAGER, ADMIN)
- **Бронирование столов** - создание, просмотр и обновление бронирований
- **Управление кафе** - создание кафе, управление менеджерами
- **Управление столами** - создание столов с указанием количества мест
- **Временные слоты** - настройка доступных временных интервалов для бронирования
- **Email уведомления** - автоматическая отправка уведомлений о создании/обновлении бронирований
- **Загрузка фото** - загрузка и хранение фотографий кафе
- **Напоминания** - автоматические напоминания за 60 минут до начала бронирования и сразу после бронирования

## Технологический стек

- **Backend**: FastAPI 0.115+
- **База данных**: PostgreSQL (SQLAlchemy 2.0+ с asyncpg)
- **Миграции**: Alembic
- **Асинхронные задачи**: Celery 5.6.1 + RabbitMQ
- **Email**: FastAPI-Mail
- **Аутентификация**: JWT (PyJWT)
- **Хеширование паролей**: pwdlib с Argon2
- **Логирование**: Loguru
- **Валидация**: Pydantic Settings
- **Обработка изображений**: Pillow
- **Reverse Proxy**: Nginx
- **Мониторинг**: Flower (Celery dashboard)

## Структура проекта

```
.
├── src/                    # Исходный код приложения
│   ├── app/               # Основной код приложения
│   │   ├── api/           # API endpoints и роутеры
│   │   │   └── endpoints/ # Эндпоинты: auth, booking, cafe, slot, table, photo, users
│   │   ├── core/          # Ядро приложения (config, db, logging, celery)
│   │   ├── crud/          # CRUD операции для моделей
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── schemas/       # Pydantic схемы
│   │   ├── tasks/         # Celery задачи
│   │   ├── utils/         # Утилиты
│   │   └── main.py        # Точка входа приложения
│   └── alembic/           # Миграции базы данных
├── infra/                 # Инфраструктура
│   ├── docker-compose.dev.yml          # Docker Compose для разработки
│   ├── docker-compose.local.yml        # Docker Compose для preprod для локального тестирования всех контейнеров
│   ├── docker-compose.production.yml   # Docker Compose для production
│   └── startup.bash       # Скрипт запуска с миграциями
├── nginx/                 # Конфигурация Nginx
├── tests/                 # Тесты
├── documentation/         # Документация
├── Dockerfile             # Docker образ приложения
├── requirements.txt       # Основные зависимости
├── requirements_style.txt # Зависимости для стилизации
├── ruff.toml             # Конфигурация Ruff
├── LOCAL_DEVELOPMENT.md  # Инструкции по локальной разработке
└── PRODUCTION.md         # Инструкции по деплою в production
```

## Основные модели данных

- **User** - пользователи системы (USER, MANAGER, ADMIN)
- **Cafe** - кафе с адресом, телефоном, описанием и фото
- **Table** - столы в кафе с указанием количества мест
- **Slot** - временные слоты для бронирования (например, 10:00-12:00)
- **Booking** - бронирования столов пользователями
- **BookingTableSlot** - связь между бронированием, столом и слотом
- **Photo** - загруженные фотографии
- **Dish** - блюда


### Предварительные требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL (или использование Docker Compose)

## Локальная разработка

Подробные инструкции см. в [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

## API Endpoints

### Аутентификация (`/auth`)
- `POST /auth/register` - регистрация нового пользователя
- `POST /auth/login` - вход в систему (получение JWT токена)
- `GET /auth/me` - информация о текущем пользователе

### Бронирования (`/booking`)
- `GET /booking` - список бронирований (с фильтрацией)
- `POST /booking` - создание бронирования
- `GET /booking/{booking_id}` - получение бронирования по ID
- `PATCH /booking/{booking_id}` - обновление бронирования

### Кафе (`/cafe`)
- `GET /cafe` - список кафе
- `POST /cafe` - создание кафе (ADMIN)
- `GET /cafe/{cafe_id}` - получение кафе по ID
- `PATCH /cafe/{cafe_id}` - обновление кафе
- `DELETE /cafe/{cafe_id}` - удаление кафе

### Столы (`/table`)
- `GET /table/cafe/{cafe_id}/tables` - список столов кафе
- `POST /table/cafe/{cafe_id}/tables` - создание стола
- `GET /table/{table_id}` - получение стола по ID
- `PATCH /table/{table_id}` - обновление стола
- `DELETE /table/{table_id}` - удаление стола

### Слоты (`/slot`)
- `GET /slot/cafe/{cafe_id}/time_slots` - список слотов кафе
- `POST /slot/cafe/{cafe_id}/time_slots` - создание слота
- `GET /slot/{slot_id}` - получение слота по ID
- `PATCH /slot/{slot_id}` - обновление слота
- `DELETE /slot/{slot_id}` - удаление слота

### Фото (`/photo`)
- `POST /photo/media` - загрузка фото
- `GET /photo/media/{media_id}` - получение фото по ID

### Пользователи (`/users`)
- `GET /users` - список пользователей (ADMIN/MANAGER)
- `GET /users/{user_id}` - получение пользователя по ID
- `PATCH /users/{user_id}` - обновление пользователя

## Роли и права доступа

### USER (Пользователь)
- Создание и управление собственными бронированиями
- Просмотр информации о кафе, столах и слотах
- Ограниченный доступ к собственным данным

### MANAGER (Менеджер)
- Все права USER
- Управление кафе, которыми назначен менеджером
- Просмотр всех бронирований в управляемых кафе
- Получение уведомлений о новых бронированиях

### ADMIN (Администратор)
- Полный доступ ко всем ресурсам
- Управление пользователями
- Создание и управление кафе
- Просмотр всех бронирований

## Стилистика кода

Для стилизации кода используется **Ruff** и **Pre-commit**.

### Проверка стилистики

```bash
ruff check
```

### Автоматическое исправление

```bash
ruff check --fix
```

## Миграции базы данных
### Создание новой миграции

```bash
cd src
alembic revision --autogenerate -m "Initial structure" --rev-id 01
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

## Логирование

Приложение использует Loguru для логирования. Уровень логирования настраивается через переменную окружения `LOGLEVEL` (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Email уведомления

Система отправляет email уведомления:
- Менеджерам кафе при создании/обновлении бронирования
- Пользователям при создании/обновлении их бронирования
- Напоминания пользователям за 60 минут до начала бронирования

В локальной разработке используется Mailpit для тестирования email. В production настройте реальный SMTP сервер через переменные окружения `MAIL_*`.

## Деплой preprod локально

Перед тем, как сделать deploy в prod, нужно собрать все контейнеры и запустить проект локально.

```bash
cd infra
docker compose -f docker-compose.local.yml up -d --build
```


## Деплой в production

Подробные инструкции по деплою в production окружение описаны в [PRODUCTION.md](PRODUCTION.md).

## Заметки о БД

### Каскадные операции на уровне ORM

Каскадные операции на уровне ORM используются **ТОЛЬКО НА СТОРОНЕ РОДИТЕЛЯ**!

Ссылка на документацию: https://docs.sqlalchemy.org/en/20/orm/cascades.html

Это означает, что мы используем параметр `cascade` в relationship только на родительской таблице, а не на дочерних.

### Пример: Table и Cafe

**Cafe имеет много Table:**

```python
tables: Mapped[list['Table']] = relationship(
    'Table',
    back_populates='cafe',
    lazy='selectin',
    cascade='save-update, merge, delete',
    passive_deletes=True,  # используется, чтобы не дублировать на уровне ORM DB-уровень ondelete='CASCADE'
    order_by='Table.seat_number',
)
```

**Table имеет один Cafe:**

```python
cafe: Mapped['Cafe'] = relationship(
    'Cafe',
    back_populates='tables',
    lazy='joined',
    # cascade здесь не нужен!
)
```

### M2M (Многие-ко-многим)

Таблица `dish_cafes` - это связь многие-ко-многим между таблицами `Dish` и `Cafe`.

```python
dish_cafes = Table(
    "dish_cafes",
    Base.metadata,
    Column(
        "dish_id",
        ForeignKey("dishes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "cafe_id",
        ForeignKey("cafes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
```

В этой M2M таблице используется составной первичный ключ из `dish_id` и `cafe_id`. Уникальное ограничение не требуется, так как составной ключ сам по себе ограничивает дубликаты.

Документация: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many