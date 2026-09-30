"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://ecom:ecom123@localhost:5434/ecom_orders"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "orders"

    SYNC_QUEUE: str = "order_sync"
    SYNC_MAX_RETRIES: int = 5
    SYNC_RETRY_BASE_DELAY: int = 10  # seconds, multiplied exponentially


settings = Settings()

ORDER_STATUSES = ("pending", "processing", "shipped", "delivered", "cancelled")
