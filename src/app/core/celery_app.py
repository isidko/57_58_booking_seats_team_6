from celery import Celery

celery_app = Celery("app", include=["app.tasks.email"])

# Подтягиваем все параметры из app.core.celery_config
celery_app.config_from_object("app.core.celery_config")
