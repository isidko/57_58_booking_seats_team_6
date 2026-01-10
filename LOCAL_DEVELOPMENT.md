## Локальная разработка

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

### 1. Запуск инфраструктуры

Для локальной разработки используйте `docker-compose.dev.yml`:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Будут подняты следующие сервисы:

* **RabbitMQ**
* **PostgreSQL**
* **Mailpit**

> В `docker-compose.dev.yml` опубликованы порты для отладки ВСЕХ сервисов с хоста.

---

### 2. Запуск приложения

Перейдите в директорию `src/` и запустите приложение:

```bash
python -m app.main
```

---

### 3. Запуск Celery worker

В отдельном терминале выполните:

```bash
celery -A app.core.celery_app:celery_app worker -l info
```

---

### 4. Запуск Flower (Celery dashboard)

Для запуска панели мониторинга Celery:

```bash
celery -A app.core.celery_app:celery_app flower
```

---

### 5. Доступные dashboard'ы

После запуска сервисов будут доступны:

* **RabbitMQ Management UI**: [http://0.0.0.0:15672](http://0.0.0.0:15672)
* **Flower (Celery)**: [http://0.0.0.0:5555](http://0.0.0.0:5555)
* **Mailpit**: [http://0.0.0.0:8025](http://0.0.0.0:8025)
* **Database**: 0.0.0.0:5432 - можно подключиться к базе с хоста
