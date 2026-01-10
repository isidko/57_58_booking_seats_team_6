# Деплой в production

## Предварительные требования

* Docker и Docker Compose установлены на сервере
* Доступ к серверу по SSH
* Настроенные секреты в GitHub Actions:
    * SSH-ключи
    * Docker Hub токены
---

## 1. Подготовка сервера

### 1.1. Установка Docker и Docker Compose

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

---

### 1.2. Подготовка файла `.env`

⚠️ **Важно:**
Файл `.env` должен храниться **только у разработчика / администратора** и **не должен коммититься в репозиторий**.
В данном репозитории он закоммичен **только для примера**.

Процесс деплоя полностью автоматизирован через **GitHub Actions**.
Администратору необходимо выполнить **только два шага**.

#### Шаг 1. Скопировать `.env` на сервер

Скопируйте подготовленный `.env` файл на сервер в директорию:
```
/home/yc-user/app
```
```bash
scp -i path/to/private/key .env yc-user@<server-ip>:/home/yc-user/app/.env
```
---
#### Шаг 2. Сделать commit и push

```bash
git add .
git commit -m "Deploy to production"
git push origin main      # или git push origin develop
```
После этого **GitHub Actions автоматически выполнит деплой**.

## 3. Структура сервисов после деплоя

После успешного деплоя на сервере будут запущены следующие сервисы:

| Сервис     | Описание           | Порт              | Доступ             |
| ---------- | ------------------ | ----------------- |--------------------|
| `server`   | FastAPI приложение | 8000 (внутренний) | Через Nginx        |
| `nginx`    | Reverse proxy      | 80                | Публичный          |
| `db`       | PostgreSQL         | 5432 (внутренний) | Только внутри сети |
| `rabbitmq` | Брокер сообщений   | 5672, 15672       | 15672 — публичный  |
| `worker`   | Celery worker      | —                 | Внутренний         |
| `flower`   | Мониторинг Celery  | 5555              | Публичный          |
| `mailpit`  | SMTP тестирование  | 8025              | Публичный          |

---

## 5. Проверка работоспособности

После завершения деплоя доступность сервисов:

* **API**:
  [http://your-server-ip/](http://your-server-ip/)
* **Swagger (API Docs)**:
  [http://your-server-ip/docs](http://your-server-ip/docs)
* **RabbitMQ Management**:
  [http://your-server-ip:15672](http://your-server-ip:15672)
* **Flower**:
  [http://your-server-ip:5555](http://your-server-ip:5555)
* **Mailpit**:
  [http://your-server-ip:8025](http://your-server-ip:8025)
