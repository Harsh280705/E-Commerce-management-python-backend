"""Order endpoints. PostgreSQL is the source of truth.

Write path: commit to PostgreSQL FIRST, then publish the sync task to
RabbitMQ. ES is never part of the synchronous request.
Read path for a single order: canonical data from PostgreSQL.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.config import ORDER_STATUSES
from app.core.database import get_db
from app.core.messaging import publish_order_sync
from app.models.models import Order, OrderItem, Product, User
from app.schemas.schemas import OrderCreate, OrderItemOut, OrderOut, OrderStatusUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _serialize(order: Order) -> OrderOut:
    items = [
        OrderItemOut(
            id=it.id,
            product_id=it.product_id,
            product_title=it.product.title if it.product else "",
            quantity=it.quantity,
            price=float(it.price),
        )
        for it in order.items
    ]
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        customer_name=order.user.name if order.user else "",
        status=order.status,
        total=float(order.total),
        created_at=order.created_at,
        items=items,
    )


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product_ids = [i.product_id for i in payload.items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    by_id = {p.id: p for p in products}
    missing = [pid for pid in product_ids if pid not in by_id]
    if missing:
        raise HTTPException(status_code=404, detail=f"Products not found: {missing}")

    order = Order(user_id=user.id, status="pending", total=0)
    db.add(order)
    db.flush()  # assign order.id inside the transaction

    total = 0.0
    for item in payload.items:
        product = by_id[item.product_id]
        line_total = float(product.price) * item.quantity
        total += line_total
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price,
            )
        )
    order.total = round(total, 2)
    db.commit()

    # ONLY AFTER successful commit: publish sync task to RabbitMQ.
    if not publish_order_sync(order.id):
        logger.warning("Order %s committed but sync publish failed; will need replay", order.id)

    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.user))
        .filter(Order.id == order.id)
        .first()
    )
    return _serialize(order)


@router.get("", response_model=list[OrderOut])
def list_orders(
    user_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if status and status not in ORDER_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {ORDER_STATUSES}")
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.user)
    )
    if user_id is not None:
        query = query.filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.id.desc()).offset((page - 1) * size).limit(size).all()
    return [_serialize(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Canonical order details — always from PostgreSQL, never ES."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.user))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize(order)


@router.put("/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status
    db.commit()

    if not publish_order_sync(order.id):
        logger.warning(
            "Order %s status committed but sync publish failed; will need replay", order.id
        )

    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product), joinedload(Order.user))
        .filter(Order.id == order_id)
        .first()
    )
    return _serialize(order)
