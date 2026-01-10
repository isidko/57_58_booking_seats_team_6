# Booking Seats API

API для системы бронирования столов в кафе. Позволяет пользователям бронировать столы в кафе на определенные временные слоты, управлять бронированиями и получать уведомления по email.

## Технологический стек
- **Асинхронные задачи**: Celery 5.6.1 + RabbitMQ
- **Аутентификация**: JWT (PyJWT)
- **Логирование**: Loguru
- **Мониторинг**: Flower (Celery dashboard)

## Локальная разработка

Подробные инструкции см. в [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)

### Проверка стилистики
```bash
ruff check
```
```bash
ruff check --fix
```

## Миграции базы данных
```bash
cd src
alembic revision --autogenerate -m "Initial structure" --rev-id 01
```
```bash
alembic upgrade head
```
```bash
alembic downgrade -1
alembic downgrade base - все миграции откатить
```

## Деплой preprod локально
Перед тем, как сделать deploy в prod, нужно собрать все контейнеры и запустить проект локально.
```bash
cd infra
docker compose -f docker-compose.local.yml up -d --build
```
После чего можно зайти на localhost:8000/docs

## Деплой в production
Подробные инструкции по деплою в production см в [PRODUCTION.md](PRODUCTION.md).

## CI

CI см в .github/workflows/deploy.yml