"""FastAPI application entrypoint for the order-management service."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from order_management.models import (
    HealthResponse,
    Order,
    OrderCreateRequest,
    OrderStatus,
    OrderStatusUpdateRequest,
    TableBill,
)
from order_management.store import (
    InvalidStatusTransitionError,
    OrderAlreadyPaidError,
    OrderNotFoundError,
    OrderStore,
)


def create_app() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    application = FastAPI(title="order-management", version="0.1.0")
    store = OrderStore()

    @application.exception_handler(OrderNotFoundError)
    async def handle_not_found(_request: Request, exc: OrderNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @application.exception_handler(InvalidStatusTransitionError)
    async def handle_invalid_transition(
        _request: Request, exc: InvalidStatusTransitionError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.exception_handler(OrderAlreadyPaidError)
    async def handle_already_paid(
        _request: Request, exc: OrderAlreadyPaidError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Return service health status."""
        return HealthResponse(status="ok", service="order-management")

    @application.post(
        "/orders",
        response_model=Order,
        status_code=status.HTTP_201_CREATED,
    )
    def create_order(payload: OrderCreateRequest) -> Order:
        """Create a dine-in or takeout order."""
        return store.create_order(payload)

    @application.get("/orders", response_model=list[Order])
    def list_orders(
        table_id: str | None = None,
        status: OrderStatus | None = None,
    ) -> list[Order]:
        """List orders with optional table_id and status filters."""
        return store.list_orders(table_id=table_id, status=status)

    @application.get("/orders/{order_id}", response_model=Order)
    def get_order(order_id: str) -> Order:
        """Get a single order by ID."""
        return store.get_order(order_id)

    @application.patch("/orders/{order_id}/status", response_model=Order)
    def update_order_status(order_id: str, payload: OrderStatusUpdateRequest) -> Order:
        """Update an order's kanban status."""
        return store.update_status(order_id, payload.status)

    @application.get("/tables/{table_id}/bill", response_model=TableBill)
    def get_table_bill(table_id: str) -> TableBill:
        """Get unpaid bill summary for a table."""
        return store.get_table_bill(table_id)

    @application.post("/orders/{order_id}/mark-paid", response_model=Order)
    def mark_order_paid(order_id: str) -> Order:
        """Mark an order as paid."""
        return store.mark_paid(order_id)

    return application


app = create_app()
