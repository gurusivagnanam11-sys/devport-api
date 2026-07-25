from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "devport",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "cleanup-old-webhook-deliveries-daily": {
        "task": "app.webhooks.tasks.cleanup_old_deliveries",
        "schedule": crontab(hour=3, minute=0),  # 3 AM UTC daily
    },
}
