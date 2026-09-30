"""FastAPI entrypoint: REST API, validation, PostgreSQL ops, sync publishing."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import orders, products, search, users
from app.core.database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models  # noqa: F401  (register models)

    Base.metadata.create_all(bind=engine)
    logger.info("Ensured PostgreSQL tables exist")
    yield


app = FastAPI(title="E-Commerce Order Management API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local Vite dev server.
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Nginx reverse proxy (docker compose: host port 80).
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(search.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
