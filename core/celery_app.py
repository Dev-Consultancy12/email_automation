from celery import Celery
from core.config import settings

celery_app = Celery(
    "antigravity",
    broker=settings.REDIS_URL,
    include=["tasks.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
