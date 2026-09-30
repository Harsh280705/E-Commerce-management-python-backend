````markdown
# E-Commerce Order Management & Search Service

Dual-writing order service: FastAPI + PostgreSQL (source of truth), RabbitMQ + Celery background sync, Elasticsearch search index, Vue.js storefront + admin.

## Architecture (Option A only)

```text
Vue.js → FastAPI → PostgreSQL → RabbitMQ → Celery → PostgreSQL (re-read) → Elasticsearch
                      ↑ canonical                     ↑ search-optimized copies only
Admin search: Vue.js → FastAPI → Elasticsearch
Order details: Vue.js → FastAPI → PostgreSQL
````

PostgreSQL commits happen **before** any sync task is published. ES failures never roll back PG; Celery retries with exponential backoff. ES doc id = PG order id (idempotent upserts).

## Tech stack

Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Pydantic · Messaging: RabbitMQ + Celery · Search: Elasticsearch · Frontend: Vue 3 + Vite + Vue Router.

## Project structure

```text
backend/app/{api,core,models,schemas,services,tasks,main.py,seed.py}
backend/{celery_app.py,requirements.txt,tests/}
frontend/src/{components,views,router,services}
docker-compose.yml · .env.example · README.md
```

## Prerequisites

Docker + Docker Compose, Python 3.11+, Node 18+.

## Setup

```powershell
docker compose up -d                      # postgres :5434, rabbitmq :5672/:15672, es :9200
cd backend
pip install -r requirements.txt
python -m app.seed                         # demo users + products
```

## Run

```powershell
# terminal 1 — API (port 8001; 8000 is commonly taken by other local apps)
cd backend; uvicorn app.main:app --reload --port 8001

# terminal 2 — Celery worker (RabbitMQ broker, order_sync queue; --pool=solo on Windows)
cd backend; celery -A celery_app.celery worker --pool=solo --loglevel=info -Q order_sync

# terminal 3 — frontend
cd frontend; npm install; npm run dev      # http://localhost:5173
```

RabbitMQ UI: [http://localhost:15672](http://localhost:15672) (guest/guest). ES: [http://localhost:9200](http://localhost:9200).

## Environment variables

See `.env.example`: `DATABASE_URL`, `RABBITMQ_URL`, `CELERY_BROKER_URL`, `ELASTICSEARCH_URL`, `ELASTICSEARCH_INDEX`.

## Tests

```powershell
cd backend; python -m pytest tests -q
cd frontend; npm run build
```


