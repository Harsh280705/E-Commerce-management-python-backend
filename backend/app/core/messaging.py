"""Publish order-sync tasks to RabbitMQ (via Celery broker).

PostgreSQL is the source of truth. This module only tells the worker
*what* to synchronize (the order id); the worker re-reads the latest
row state from PostgreSQL. It must be called ONLY after a successful commit.
"""

import logging

logger = logging.getLogger(__name__)


def publish_order_sync(order_id: int) -> bool:
    """Enqueue ``sync_order_to_elasticsearch(order_id)``.

    Returns True when the message was accepted by the broker, False otherwise.
    A False return must NOT roll back the already-committed PostgreSQL
    transaction — the order is safe; sync can be retried/replayed later.
    """
    try:
        # Local import avoids a hard Celery dependency at API import time
        # (e.g. unit tests that never publish).
        from app.tasks.sync import sync_order_to_elasticsearch

        sync_order_to_elasticsearch.apply_async(args=[order_id])
        logger.info("Published sync task for order %s", order_id)
        return True
    except Exception:  # noqa: BLE001 - broker down must not break the request
        logger.exception("Failed to publish sync task for order %s", order_id)
        return False
