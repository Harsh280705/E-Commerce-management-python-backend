"""Backend tests: PG writes, sync publishing, ES upsert/idempotency/retries, search, validation.

Run:  pytest -q   (from backend/)
Uses SQLite + dependency override; ES and broker calls are mocked so no
infrastructure is required.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.models import Product, User

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(User(id=1, name="Harsh Patel", email="harsh@example.com"))
    db.add(Product(id=1, sku="SKU-1", title="Keyboard", description="kbd", price=100.0))
    db.add(Product(id=2, sku="SKU-2", title="Mouse", description="mouse", price=50.0))
    db.commit()
    db.close()
    yield


def _db():
    return TestingSession()


def test_product_creation():
    r = client.post(
        "/api/products",
        json={"sku": "SKU-9", "title": "Hub", "description": "hub", "price": 10.5},
    )
    assert r.status_code == 201
    assert r.json()["sku"] == "SKU-9"


def test_order_creation_stored_in_postgres_and_publishes_task():
    with patch("app.api.orders.publish_order_sync", return_value=True) as pub:
        r = client.post(
            "/api/orders",
            json={"user_id": 1, "items": [{"product_id": 1, "quantity": 2}]},
        )
    assert r.status_code == 201
    data = r.json()
    assert data["total"] == 200.0
    assert data["status"] == "pending"
    pub.assert_called_once_with(data["id"])
    # stored in PostgreSQL
    db = _db()
    try:
        from app.models.models import Order

        order = db.query(Order).filter(Order.id == data["id"]).first()
        assert order is not None and float(order.total) == 200.0
        assert len(order.items) == 1
    finally:
        db.close()


def test_sync_task_builds_es_document_and_upserts_by_order_id():
    with patch("app.api.orders.publish_order_sync", return_value=True):
        order_id = client.post(
            "/api/orders", json={"user_id": 1, "items": [{"product_id": 2, "quantity": 3}]}
        ).json()["id"]
    from app.tasks.sync import sync_order_to_elasticsearch

    fake_es = MagicMock()
    with (
        patch("app.tasks.sync.SessionLocal", TestingSession),
        patch("app.tasks.sync.get_es_client", return_value=fake_es),
        patch("app.tasks.sync.ensure_order_index", return_value=None),
    ):
        sync_order_to_elasticsearch.run(order_id)
    assert fake_es.index.call_count == 1
    _, kwargs = fake_es.index.call_args
    assert kwargs["id"] == str(order_id)  # PG id == ES document id
    assert kwargs["document"]["order_id"] == order_id
    assert kwargs["document"]["customer_name"] == "Harsh Patel"


def test_repeated_sync_updates_same_document_no_duplicates():
    with patch("app.api.orders.publish_order_sync", return_value=True):
        order_id = client.post(
            "/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 1}]}
        ).json()["id"]
    from app.tasks.sync import sync_order_to_elasticsearch

    store: dict = {}

    class FakeES:
        def index(self, index, id, document):
            store[id] = document

    with (
        patch("app.tasks.sync.SessionLocal", TestingSession),
        patch("app.tasks.sync.get_es_client", return_value=FakeES()),
        patch("app.tasks.sync.ensure_order_index", return_value=None),
    ):
        sync_order_to_elasticsearch.run(order_id)
        sync_order_to_elasticsearch.run(order_id)
        sync_order_to_elasticsearch.run(order_id)
    assert list(store.keys()) == [str(order_id)]  # single logical document


def test_es_timeout_triggers_retry_not_rollback():
    """ES failure must retry; the committed PG order must survive."""
    with patch("app.api.orders.publish_order_sync", return_value=True):
        order_id = client.post(
            "/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 1}]}
        ).json()["id"]
    from app.models.models import Order
    from app.tasks.sync import sync_order_to_elasticsearch

    fake_es = MagicMock()
    fake_es.index.side_effect = TimeoutError("es timed out")
    with (
        patch("app.tasks.sync.SessionLocal", TestingSession),
        patch("app.tasks.sync.get_es_client", return_value=fake_es),
        patch("app.tasks.sync.ensure_order_index", return_value=None),
        patch.object(sync_order_to_elasticsearch, "retry", side_effect=Exception("retry-called")) as do_retry,
    ):
        try:
            sync_order_to_elasticsearch.run(order_id)
        except Exception as e:
            assert str(e) == "retry-called"
        assert do_retry.call_count == 1
        assert "countdown" in do_retry.call_args.kwargs  # backoff delay set
    # PG order untouched by the ES failure
    db = _db()
    try:
        assert db.query(Order).filter(Order.id == order_id).first() is not None
    finally:
        db.close()


def test_status_update_publishes_sync_and_reflects_in_es_doc():
    with patch("app.api.orders.publish_order_sync", return_value=True):
        order_id = client.post(
            "/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 1}]}
        ).json()["id"]
    with patch("app.api.orders.publish_order_sync", return_value=True) as pub:
        r = client.put(f"/api/orders/{order_id}/status", json={"status": "shipped"})
    assert r.status_code == 200 and r.json()["status"] == "shipped"
    pub.assert_called_once_with(order_id)

    from app.tasks.sync import sync_order_to_elasticsearch

    captured: dict = {}

    class FakeES:
        def index(self, index, id, document):
            captured.update(document)

    with (
        patch("app.tasks.sync.SessionLocal", TestingSession),
        patch("app.tasks.sync.get_es_client", return_value=FakeES()),
        patch("app.tasks.sync.ensure_order_index", return_value=None),
    ):
        sync_order_to_elasticsearch.run(order_id)
    assert captured["status"] == "shipped"


def test_search_queries_elasticsearch():
    fake_resp = {"hits": {"total": {"value": 1}, "hits": [
        {"_score": 1.0, "_source": {"order_id": 1, "status": "pending"}}]}}
    fake_es = MagicMock()
    fake_es.search.return_value = fake_resp
    with patch("app.services.search_service.get_es_client", return_value=fake_es):
        r = client.get("/api/search/orders", params={"q": "harsh"})
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_search_by_order_id_and_status_filter():
    fake_es = MagicMock()
    fake_es.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    with patch("app.services.search_service.get_es_client", return_value=fake_es):
        r = client.get("/api/search/orders", params={"order_id": 1024, "status": "delivered"})
    assert r.status_code == 200
    body = fake_es.search.call_args.kwargs["body"]
    assert "delivered" in str(body) and "1024" in str(body)


def test_validation_errors():
    assert client.post("/api/orders", json={"user_id": 999, "items": [{"product_id": 1, "quantity": 1}]}).status_code == 404
    assert client.post("/api/orders", json={"user_id": 1, "items": [{"product_id": 999, "quantity": 1}]}).status_code == 404
    assert client.post("/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 0}]}).status_code == 422
    with patch("app.api.orders.publish_order_sync", return_value=True):
        oid = client.post("/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 1}]}).json()["id"]
    assert client.put(f"/api/orders/{oid}/status", json={"status": "bogus"}).status_code == 422


def test_end_to_end_postgres_to_search():
    """Create order -> PG -> (mocked broker) sync task -> ES doc -> search hit."""
    published: list = []
    with patch("app.api.orders.publish_order_sync", side_effect=lambda oid: published.append(oid) or True):
        order_id = client.post(
            "/api/orders", json={"user_id": 1, "items": [{"product_id": 1, "quantity": 2}]}
        ).json()["id"]
    assert published == [order_id]

    from app.tasks.sync import sync_order_to_elasticsearch

    es_store: dict = {}

    class FakeES:
        def index(self, index, id, document):
            es_store[id] = document

        def search(self, index, body):
            docs = [d for d in es_store.values()
                    if "harsh" in d.get("customer_name", "").lower()]
            return {"hits": {"total": {"value": len(docs)},
                             "hits": [{"_score": 1.0, "_source": d} for d in docs]}}

    fake = FakeES()
    with (
        patch("app.tasks.sync.SessionLocal", TestingSession),
        patch("app.tasks.sync.get_es_client", return_value=fake),
        patch("app.tasks.sync.ensure_order_index", return_value=None),
        patch("app.services.search_service.get_es_client", return_value=fake),
    ):
        sync_order_to_elasticsearch.run(order_id)  # RabbitMQ -> Celery -> ES
        r = client.get("/api/search/orders", params={"q": "harsh"})
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["results"][0]["order_id"] == order_id
