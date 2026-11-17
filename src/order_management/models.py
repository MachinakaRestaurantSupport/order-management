"""Domain models and status transition rules for order management."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OrderSource = Literal["dine_in", "takeout"]
OrderStatus = Literal["received", "preparing", "ready", "served"]

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    "received": {"preparing"},
    "preparing": {"ready"},
    "ready": {"served"},
    "served": set(),
}


class OrderItemInput(BaseModel):
    """Input line item for an order."""

    product_id: str
    product_name: str
    unit_price: int = Field(ge=0)
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    """Request payload for creating a new order."""

    source: OrderSource
    table_id: str | None = None
    session_id: str | None = None
    customer_id: str | None = None
    pickup_at: str | None = None
    is_takeout_from_table: bool = False
    items: list[OrderItemInput] = Field(min_length=1)


class OrderStatusUpdateRequest(BaseModel):
    """Request payload for updating an order kanban status."""

    status: OrderStatus


class Order(BaseModel):
    """Persisted order representation."""

    order_id: str
    source: OrderSource
    table_id: str | None = None
    session_id: str | None = None
    customer_id: str | None = None
    pickup_at: str | None = None
    is_takeout_from_table: bool = False
    items: list[OrderItemInput]
    total_amount: int
    status: OrderStatus = "received"
    paid: bool = False
    created_at: datetime


class TableBill(BaseModel):
    """Unpaid bill summary for a dining table."""

    table_id: str
    order_ids: list[str]
    total_amount: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
