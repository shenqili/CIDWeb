from celery import Celery

from .config import get_settings

settings = get_settings()

celery_app = Celery(
    "cidweb",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone=settings.timezone,
    enable_utc=False,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


@celery_app.task(name="cidweb.healthcheck")
def healthcheck_task():
    return {"status": "ok"}
