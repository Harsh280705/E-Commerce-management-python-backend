"""Elasticsearch-backed admin order search (search path only).

Full order details always come from PostgreSQL; this module powers the
fast search/filter listing via the flattened ES documents.
"""

import logging

from app.core.config import settings
from app.core.search import get_es_client

logger = logging.getLogger(__name__)


def search_orders(
    q: str | None = None,
    status: str | None = None,
    customer: str | None = None,
    order_id: int | None = None,
    sort: str = "newest",
    page: int = 1,
    size: int = 20,
) -> dict:
    es = get_es_client()
    must: list[dict] = []
    filters: list[dict] = []

    if order_id is not None:
        filters.append({"term": {"order_id": order_id}})
    if status:
        filters.append({"term": {"status": status}})
    if customer:
        must.append(
            {
                "multi_match": {
                    "query": customer,
                    "fields": ["customer_name^2", "customer_email"],
                }
            }
        )
    if q:
        # Plain order-id search ("1024" / "ORD-1024") -> exact order_id filter.
        digits = "".join(ch for ch in q if ch.isdigit())
        if digits and (q.strip().isdigit() or q.strip().upper().startswith("ORD")):
            try:
                filters.append({"term": {"order_id": int(digits)}})
            except ValueError:
                pass
        else:
            must.append(
                {
                    "multi_match": {
                        "query": q,
                        "fields": [
                            "customer_name^3",
                            "customer_email^2",
                            "status^2",
                            "items.title^2",
                        ],
                    }
                }
            )

    query: dict = {"bool": {}}
    if must:
        query["bool"]["must"] = must
    if filters:
        query["bool"]["filter"] = filters
    if not query["bool"]:
        query = {"match_all": {}}

    sort_clause = [{"order_date": {"order": "desc"}}]
    if sort == "oldest":
        sort_clause = [{"order_date": {"order": "asc"}}]
    elif sort == "total_desc":
        sort_clause = [{"total_amount": {"order": "desc"}}]
    elif sort == "total_asc":
        sort_clause = [{"total_amount": {"order": "asc"}}]

    body = {
        "query": query,
        "sort": sort_clause,
        "from": (page - 1) * size,
        "size": size,
    }
    resp = es.search(index=settings.ELASTICSEARCH_INDEX, body=body)
    hits = resp.get("hits", {})
    results = []
    for h in hits.get("hits", []):
        src = h.get("_source", {})
        src["score"] = h.get("_score")
        results.append(src)
    total = hits.get("total", {}).get("value", 0)
    return {"total": total, "page": page, "size": size, "results": results}
