"""Background synchronization: PostgreSQL -> Elasticsearch (Option A dual-write).

Flow: FastAPI commits to PostgreSQL, publishes order id to RabbitMQ.
This task consumes the id, re-reads the LATEST rows from PostgreSQL,
builds the flattened ES document and upserts it with ``_id = order_id``
(idempotent: repeats overwrite the same document).

ES failures NEVER roll back PostgreSQL; the task retries with
exponential backoff up to SYNC_MAX_RETRIES.
"""

import logging

from celery.exceptions import Retry

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.search import ensure_order_index, get_es_client
from app.services.documents import build_order_document
from celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(
    bind=True,
    name="app.tasks.sync.sync_order_to_elasticsearch",
    max_retries=settings.SYNC_MAX_RETRIES,
)
def sync_order_to_elasticsearch(self, order_id: int) -> dict:
    try:
        ensure_order_index()
    except Exception as exc:  # ES down at index-ensure time -> retry
        countdown = settings.SYNC_RETRY_BASE_DELAY * (2**self.request.retries)
        logger.warning(
            "ES index ensure failed for order %s (attempt %s/%s): %s. Retrying in %ss",
            order_id,
            self.request.retries + 1,
            settings.SYNC_MAX_RETRIES,
            exc,
            countdown,
        )
        raise self.retry(exc=exc, countdown=countdown)

    db = SessionLocal()
    try:
        doc = build_order_document(db, order_id)
    finally:
        db.close()

    if doc is None:
        logger.warning("Order %s not found in PostgreSQL; nothing to sync", order_id)
        return {"order_id": order_id, "synced": False, "reason": "not_found"}

    try:
        es = get_es_client()
        # Idempotent upsert: document ID == PostgreSQL order ID.
        es.index(index=settings.ELASTICSEARCH_INDEX, id=str(order_id), document=doc)
        logger.info("Synchronized order %s to Elasticsearch", order_id)
        return {"order_id": order_id, "synced": True}
    except Retry:
        raise
    except Exception as exc:  # temporary ES failure -> retry with backoff
        countdown = settings.SYNC_RETRY_BASE_DELAY * (2**self.request.retries)
        logger.warning(
            "ES sync failed for order %s (attempt %s/%s): %s. Retrying in %ss",
            order_id,
            self.request.retries + 1,
            settings.SYNC_MAX_RETRIES,
            exc,
            countdown,
        )
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except Retry:
            raise
        except Exception:
            logger.exception("Order %s sync exhausted retries", order_id)
            raise
