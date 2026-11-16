"""In-memory order store and business logic."""

from datetime import UTC, datetime
from uuid import uuid4

from order_management.models import (
    ALLOWED_TRANSITIONS,
    Order,
    OrderCreateRequest,
    OrderStatus,
    TableBill,
)


class OrderNotFoundError(LookupError):
    """Raised when an order ID does not exist."""


class InvalidStatusTransitionError(ValueError):
    """Raised when a kanban status transition is not permitted."""


class OrderAlreadyPaidError(ValueError):
    """Raised when attempting to mark an already paid order as paid."""


class OrderStore:
    """In-memory repository managing orders, kanban transitions, and billing."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}

    def create_order(self, payload: OrderCreateRequest) -> Order:
        """Register a new order and calculate its total amount."""
        total_amount = sum(item.unit_price * item.quantity for item in payload.items)
        order = Order(
            order_id=f"ord_{uuid4().hex[:12]}",
            source=payload.source,
            table_id=payload.table_id,
            session_id=payload.session_id,
            customer_id=payload.customer_id,
            pickup_at=payload.pickup_at,
            is_takeout_from_table=payload.is_takeout_from_table,
            items=list(payload.items),
            total_amount=total_amount,
            status="received",
            paid=False,
            created_at=datetime.now(UTC),
        )
        self._orders[order.order_id] = order
        return order

    def list_orders(
        self,
        table_id: str | None = None,
        status: OrderStatus | None = None,
    ) -> list[Order]:
        """List orders optionally filtered by table_id and/or status."""
        results = list(self._orders.values())
        if table_id is not None:
            results = [order for order in results if order.table_id == table_id]
        if status is not None:
            results = [order for order in results if order.status == status]
        return results

    def get_order(self, order_id: str) -> Order:
        """Retrieve a single order by ID or raise OrderNotFoundError."""
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order not found: {order_id}")
        return order

    def update_status(self, order_id: str, next_status: OrderStatus) -> Order:
        """Transition an order's kanban status if allowed."""
        order = self.get_order(order_id)
        if next_status not in ALLOWED_TRANSITIONS[order.status]:
            raise InvalidStatusTransitionError(
                f"Transition from '{order.status}' to '{next_status}' is not allowed."
            )
        updated = order.model_copy(update={"status": next_status})
        self._orders[order_id] = updated
        return updated

    def get_table_bill(self, table_id: str) -> TableBill:
        """Calculate unpaid total amount for a given table."""
        unpaid_orders = [
            order
            for order in self._orders.values()
            if order.table_id == table_id and not order.paid
        ]
        return TableBill(
            table_id=table_id,
            order_ids=[order.order_id for order in unpaid_orders],
            total_amount=sum(order.total_amount for order in unpaid_orders),
        )

    def mark_paid(self, order_id: str) -> Order:
        """Mark an unpaid order as paid, preventing duplicate payment."""
        order = self.get_order(order_id)
        if order.paid:
            raise OrderAlreadyPaidError(f"Order is already paid: {order_id}")
        updated = order.model_copy(update={"paid": True})
        self._orders[order_id] = updated
        return updated
