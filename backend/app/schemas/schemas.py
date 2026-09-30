"""Pydantic request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import ORDER_STATUSES


# ---------- Users ----------
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


# ---------- Products ----------
class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    price: float = Field(gt=0)


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)


class ProductOut(BaseModel):
    id: int
    sku: str
    title: str
    description: str
    price: float

    model_config = {"from_attributes": True}


# ---------- Orders ----------
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=1000)


class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItemIn] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def no_duplicate_products(cls, items):
        ids = [i.product_id for i in items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product_id in items")
        return items


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_title: str = ""
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    user_id: int
    customer_name: str = ""
    status: str
    total: float
    created_at: datetime | None = None
    items: list[OrderItemOut] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ORDER_STATUSES:
            raise ValueError(f"status must be one of {ORDER_STATUSES}")
        return v


# ---------- Search ----------
class SearchResultItem(BaseModel):
    order_id: int
    order_date: str | None = None
    status: str
    total_amount: float
    customer_id: int
    customer_name: str
    items: list[dict] = []
    score: float | None = None
