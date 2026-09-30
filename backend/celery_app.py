"""Celery application: RabbitMQ broker, dedicated sync queue, late-ack reliability."""

from celery import Celery

from app.core.config import settings

celery = Celery(
    "order_sync",
    broker=settings.CELERY_BROKER_URL,
    backend="rpc://",
)

celery.conf.update(
    task_acks_late=True,  # acknowledge only after successful processing
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_queue=settings.SYNC_QUEUE,
    task_routes={"app.tasks.sync.*": {"queue": settings.SYNC_QUEUE}},
    task_annotations={"app.tasks.sync.sync_order_to_elasticsearch": {"rate_limit": "50/s"}},
)

# Ensure task modules are registered with the worker.
import app.tasks.sync  # noqa: F401,E402
