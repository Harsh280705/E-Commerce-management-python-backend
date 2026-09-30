"""Seed demo users + products (idempotent). Usage: python -m app.seed"""

from app.core.database import Base, SessionLocal, engine
from app.models.models import Product, User
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.query(User).count() == 0:
        db.add_all(
            [
                User(name="Harsh Patel", email="harsh@example.com"),
                User(name="Asha Verma", email="asha@example.com"),
                User(name="Rahul Shah", email="rahul@example.com"),
            ]
        )
    if db.query(Product).count() == 0:
        db.add_all(
            [
                Product(sku="SKU-1001", title="Wireless Headphones", description="Noise-cancelling over-ear headphones", price=2999.00),
                Product(sku="SKU-1002", title="Mechanical Keyboard", description="Hot-swap RGB mechanical keyboard", price=4499.00),
                Product(sku="SKU-1003", title="Smart Watch", description="Fitness tracking smartwatch", price=5999.00),
                Product(sku="SKU-1004", title="USB-C Hub", description="7-in-1 USB-C docking hub", price=1899.00),
                Product(sku="SKU-1005", title="Laptop Stand", description="Ergonomic aluminium laptop stand", price=1299.00),
                Product(sku="SKU-1006", title="Webcam HD", description="1080p webcam with microphone", price=2499.00),
            ]
        )
    db.commit()
    print("Seeded users and products.")
finally:
    db.close()
