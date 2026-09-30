"""Admin search endpoint (Elasticsearch) + health endpoint."""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.core.config import ORDER_STATUSES
from app.core.search import get_es_client
from app.services.search_service import search_orders

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/orders")
def search_orders_endpoint(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    customer: str | None = Query(default=None),
    order_id: int | None = Query(default=None),
    sort: str = Query(default="newest"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    if status and status not in ORDER_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {ORDER_STATUSES}")
    try:
        return search_orders(
            q=q, status=status, customer=customer, order_id=order_id,
            sort=sort, page=page, size=size,
        )
    except Exception as exc:  # ES unavailable -> 503, PG data is unaffected
        logger.exception("Elasticsearch search failed")
        raise HTTPException(status_code=503, detail=f"Search unavailable: {exc}")


@router.get("/health")
def search_health():
    """Report ES + sync-index status for the admin UI sync badge."""
    try:
        es = get_es_client()
        ping = es.ping()
        count = None
        if ping:
            try:
                count = es.count(index="orders").get("count")
            except Exception:
                count = None
        return {"elasticsearch": "up" if ping else "down", "indexed_orders": count}
    except Exception as exc:
        return {"elasticsearch": "down", "error": str(exc), "indexed_orders": None}
