## Локальная разработка

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
