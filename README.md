# E-Commerce Order Management & Search Service

Order management backend with background search indexing and a Vue 3 storefront + admin UI.

**PostgreSQL is the source of truth. Elasticsearch is a search index only.**

## Tech stack

FastAPI · SQLAlchemy · Pydantic · PostgreSQL · RabbitMQ · Celery · Elasticsearch · Nginx · Vue 3 + Vite

## Architecture

```
Vue 3 → Nginx → FastAPI → PostgreSQL
                         ↓
                     RabbitMQ → Celery → Elasticsearch
```

Orders commit to PostgreSQL first, then a sync task is published to RabbitMQ. The Celery worker re-reads the latest order from PostgreSQL and upserts it into Elasticsearch (`_id` = PG order id, so repeats never duplicate). ES failures never roll back PostgreSQL; the worker retries with exponential backoff. Order details are served from PostgreSQL, admin search from Elasticsearch.

## Services (`docker-compose.yml`)

| Service | Image / build | Host port |
|---|---|---|
| `nginx` | built (`nginx/Dockerfile`: Vue build + reverse proxy) | `80` |
| `api` | built (`backend/Dockerfile`, uvicorn) | `8001` → container `8000` |
| `celery-worker` | same backend image, `order_sync` queue | — |
| `postgres` | `postgres:16-alpine` | `5434` → `5432` |
| `rabbitmq` | `rabbitmq:3-management-alpine` | `5672`, `15672` |
| `elasticsearch` | `elasticsearch:8.11.0` (single node) | `9200` |

## Run with Docker Compose

```powershell
Copy-Item .env.example .env          # first time only
docker compose up -d --build
cd backend; python -m app.seed       # demo users + products
```

Stop: `docker compose down` (add `-v` to also drop `pgdata`/`esdata`).

Local dev alternative: `docker compose up -d postgres rabbitmq elasticsearch`, then run the API (`cd backend; uvicorn app.main:app --reload --port 8001`), worker (`celery -A celery_app.celery worker --pool=solo --loglevel=info -Q order_sync`) and frontend (`cd frontend; npm install; npm run dev`) yourself.

## URLs

- App: http://localhost (via Nginx) · API direct: http://localhost:8001
- Swagger: http://localhost/docs · Health: http://localhost/api/health
- Search: http://localhost/api/search/orders?q=harsh
- RabbitMQ UI: http://localhost:15672 (guest/guest) · Elasticsearch: http://localhost:9200

## Project structure

```text
backend/app/{api,core,models,schemas,services,tasks,main.py,seed.py}
backend/{Dockerfile,celery_app.py,requirements.txt,tests/}
frontend/src/{components,views,router,services}
nginx/{Dockerfile,nginx.conf}
docker-compose.yml · .env.example
```

## Tests

```powershell
cd backend; python -m pytest tests -q   # mocked infra: PG writes, sync publish, ES upsert/idempotency/retry, search
cd frontend; npm run build
```
