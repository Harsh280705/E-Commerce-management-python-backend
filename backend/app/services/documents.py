"""Build the flattened, search-optimized ES document from relational rows."""

from sqlalchemy.orm import Session

from app.models.models import Order


def build_order_document(db: Session, order_id: int) -> dict | None:
    """Read the LATEST order state from PostgreSQL and flatten it.

    Returns None when the order does not exist.
    Uses the PostgreSQL order id as the logical identity (caller uses it
    as the Elasticsearch ``_id`` so re-syncs overwrite, never duplicate).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        return None
    items = []
    for it in order.items:
        items.append(
            {
                "product_id": it.product_id,
                "title": it.product.title if it.product else "",
                "price": float(it.price),
                "quantity": it.quantity,
            }
        )
    return {
        "order_id": order.id,
        "order_date": order.created_at.isoformat() if order.created_at else None,
        "status": order.status,
        "total_amount": float(order.total),
        "customer_id": order.user_id,
        "customer_name": order.user.name if order.user else "",
        "customer_email": order.user.email if order.user else "",
        "items": items,
    }
