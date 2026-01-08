import os

from app.core.config import settings

broker_url = (
    f"amqp://{settings.rabbitmq_default_user}:{settings.rabbitmq_default_pass}"
    f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}//"
)
result_backend = os.getenv("CELERY_RESULT_BACKEND", "rpc://")


task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

timezone = os.getenv("CELERY_TIMEZONE", "Europe/Moscow")
enable_utc = True

broker_connection_retry_on_startup = True

task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1

task_track_started = True
