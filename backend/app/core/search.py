"""Elasticsearch client + index management (search-optimized order documents)."""

import logging

from elasticsearch import Elasticsearch

from app.core.config import settings

logger = logging.getLogger(__name__)

ORDER_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "order_id": {"type": "integer"},
            "order_date": {"type": "date"},
            "status": {"type": "keyword"},
            "total_amount": {"type": "float"},
            "customer_id": {"type": "integer"},
            "customer_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "customer_email": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "items": {
                "type": "nested",
                "properties": {
                    "product_id": {"type": "integer"},
                    "title": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "price": {"type": "float"},
                    "quantity": {"type": "integer"},
                },
            },
        }
    }
}

_client: Elasticsearch | None = None


def get_es_client() -> Elasticsearch:
    global _client
    if _client is None:
        _client = Elasticsearch(settings.ELASTICSEARCH_URL, request_timeout=10)
    return _client


def ensure_order_index() -> None:
    """Create the orders index if it does not exist (idempotent)."""
    es = get_es_client()
    if not es.indices.exists(index=settings.ELASTICSEARCH_INDEX):
        es.indices.create(index=settings.ELASTICSEARCH_INDEX, body=ORDER_INDEX_MAPPING)
        logger.info("Created Elasticsearch index %s", settings.ELASTICSEARCH_INDEX)
