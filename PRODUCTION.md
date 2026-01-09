## Деплой в production

Данная инструкция описывает процесс развертывания приложения в продакшн-окружении.

### Предварительные требования

- Docker и Docker Compose установлены на сервере
- Доступ к серверу по SSH
- Настроенные секреты в GitHub Actions (SSH ключи, Docker Hub токены)

### 1. Подготовка сервера

#### 1.1. Установка Docker и Docker Compose

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка сессии (или выход/вход)
newgrp docker
```

#### 1.2. Подготовка файла .env

.env должен ъраниться в секрете у разработчика. В данном репозитории он закомичен в git для примера.

**Важно:** Убедитесь, что все секретные значения (пароли, ключи) изменены на безопасные.

### 2. Деплой приложения

Процесс деплоя полностью автоматизирован через GitHub Actions. Администратору необходимо выполнить только два шага:

#### 2.1. Копирование .env файла на сервер

Скопируйте подготовленный `.env` файл на сервер в директорию `/home/yc-user/app`:

```bash
scp .env path/to/private/key username@<server-ip>:/home/yc-user/app/.env
```

#### 2.2. Запуск деплоя

Сделайте коммит и пуш в ветку `main` или `develop`:

```bash
git add .
git commit -m "Deploy to production"
git push origin main  # или git push origin develop
```

После этого GitHub Actions автоматически выполнит весь процесс деплоя.

### 3. Схема работы CI/CD workflow

При пуше в ветки `main` или `develop` автоматически запускается workflow `build-and-deploy`, который состоит из двух:

#### 3.1. Job: `build_and_push`

Выполняется на GitHub Actions runner (Ubuntu):

1. **Checkout кода** — клонирование репозитория
2. **Настройка Docker Buildx** — подготовка окружения для сборки образов
3. **Авторизация в Docker Hub** — вход используя секреты из GitHub
4. **Сборка и публикация образа приложения**:
   - Сборка Docker-образа из `Dockerfile`
   - Публикация в Docker Hub как `{DOCKERHUB_USERNAME}/practicum-final:latest`
5. **Сборка и публикация образа Nginx**:
   - Сборка Docker-образа из `nginx/Dockerfile`
   - Публикация в Docker Hub как `{DOCKERHUB_USERNAME}/practicum-final-nginx:latest`

#### 3.2. Job: `deploy`

Выполняется после успешного завершения `build_and_push`:

1. **Checkout кода** — клонирование репозитория
2. **Создание директории на сервере**:
   - Подключение к серверу по SSH
   - Создание директории `/home/yc-user/app` (если не существует)
3. **Копирование docker-compose.production.yml**:
   - Копирование файла `infra/docker-compose.production.yml` на сервер
   - Файл размещается в `/home/yc-user/app/docker-compose.production.yml`
4. **Деплой на сервере**:
   - Подключение к серверу по SSH
   - Переход в директорию `/home/yc-user/app`
   - Выполнение команд:
     ```bash
     docker compose -f docker-compose.production.yml pull
     docker compose -f docker-compose.production.yml up -d --remove-orphans --force-recreate --pull always
     docker image prune -af
     ```

#### 3.3. Что происходит при деплое на сервере

1. **Pull образов** — загрузка последних версий образов из Docker Hub
2. **Запуск контейнеров**:
   - Остановка и удаление старых контейнеров (`--remove-orphans`)
   - Принудительное пересоздание контейнеров (`--force-recreate`)
   - Запуск всех сервисов в фоновом режиме (`-d`)
3. **Очистка** — удаление неиспользуемых Docker-образов для экономии места

#### 3.4. Автоматическое применение миграций

При старте контейнера `server` автоматически выполняется скрипт `startup.bash`, который:
1. Применяет миграции Alembic: `alembic upgrade head`
2. Запускает приложение: `python -m app.main`

### 4. Структура сервисов после деплоя

После успешного деплоя на сервере будут запущены следующие сервисы:

| Сервис | Описание | Порт | Доступ |
|--------|----------|------|--------|
| `server` | FastAPI приложение | 8000 (внутренний) | Через Nginx |
| `nginx` | Reverse proxy | 80 | Публичный |
| `db` | PostgreSQL | 5432 (внутренний) | Только внутри сети |
| `rabbitmq` | Брокер сообщений | 5672, 15672 | 15672 - управление |
| `worker` | Celery worker | - | Внутренний |
| `flower` | Мониторинг Celery | 5555 | Ограниченный доступ |
| `mailpit` | SMTP тестирование | 8025 | Для тестирования |

### 5. Проверка работоспособности

После завершения деплоя проверьте доступность сервисов:

- **API**: http://your-server-ip/
- **API Docs**: http://your-server-ip/docs
- **RabbitMQ Management**: http://your-server-ip:15672
- **Flower**: http://your-server-ip:5555
- **Mailpit**: http://your-server-ip:8025

### 6. Мониторинг деплоя

Статус деплоя можно отслеживать в разделе **Actions** вашего GitHub репозитория. Там отображаются:
- Прогресс выполнения каждого шага
- Логи выполнения
- Ошибки (если возникли)

### 7. Устранение неполадок

#### 7.1. Проблемы с деплоем

Если деплой не прошел успешно:
1. Проверьте логи в GitHub Actions
2. Убедитесь, что файл `.env` находится в `/home/yc-user/app/`
3. Проверьте доступность сервера по SSH
4. Убедитесь, что на сервере установлены Docker и Docker Compose

#### 7.2. Подключение к серверу для диагностики

```bash
ssh yc-user@<server-ip>
cd /home/yc-user/app

# Проверка статуса контейнеров
docker compose -f docker-compose.production.yml ps

# Просмотр логов
docker compose -f docker-compose.production.yml logs -f

# Проверка конкретного сервиса
docker compose -f docker-compose.production.yml logs server
```

#### 7.3. Проблемы с миграциями

Если миграции не применились автоматически:

```bash
ssh yc-user@<server-ip>
cd /home/yc-user/app
docker compose -f docker-compose.production.yml exec server alembic upgrade head
```