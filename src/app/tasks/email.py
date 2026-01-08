import asyncio
from time import sleep

from fastapi_mail import FastMail, MessageSchema

from app.core.celery_app import celery_app
from app.core.config import email_config


@celery_app.task(name="tasks.send_email", pydantic=True)
def send_email(message: MessageSchema) -> None:
    """Send email task."""
    fm = FastMail(email_config)
    sleep(5)
    asyncio.run(fm.send_message(message))
