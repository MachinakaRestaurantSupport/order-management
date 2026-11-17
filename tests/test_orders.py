"""Unit tests for the order-management FastAPI service."""

import pytest
from fastapi.testclient import TestClient

from order_management.main import create_app


@pytest.fixture()
def client() -> TestClient:
    """Provide an isolated TestClient with a fresh in-memory store per test."""
    return TestClient(create_app())


def _sample_dine_in_payload(table_id: str = "T-01") -> dict:
    return {
        "source": "dine_in",
        "table_id": table_id,
        "session_id": "sess-001",
        "items": [
            {
                "product_id": "item-1",
                "product_name": "Hamburg Steak",
                "unit_price": 1200,
                "quantity": 2,
            },
            {
                "product_id": "item-2",
                "product_name": "Iced Coffee",
                "unit_price": 450,
                "quantity": 1,
            },
        ],
    }


def test_health(client: TestClient) -> None:
    """GET /health returns service status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "order-management"}


def test_create_order_and_total_calculation(client: TestClient) -> None:
    """POST /orders creates dine_in and takeout orders with computed total_amount."""
    dine_in_resp = client.post("/orders", json=_sample_dine_in_payload())
    assert dine_in_resp.status_code == 201
    dine_in = dine_in_resp.json()
    assert dine_in["source"] == "dine_in"
    assert dine_in["table_id"] == "T-01"
    assert dine_in["total_amount"] == 2850
    assert dine_in["status"] == "received"
    assert dine_in["paid"] is False
    assert dine_in["order_id"].startswith("ord_")

    takeout_resp = client.post(
        "/orders",
        json={
            "source": "takeout",
            "customer_id": "cust-99",
            "pickup_at": "2026-11-16T18:30:00Z",
            "is_takeout_from_table": False,
            "items": [
                {
                    "product_id": "item-3",
                    "product_name": "Bento Box",
                    "unit_price": 900,
                    "quantity": 3,
                }
            ],
        },
    )
    assert takeout_resp.status_code == 201
    takeout = takeout_resp.json()
    assert takeout["source"] == "takeout"
    assert takeout["total_amount"] == 2700
    assert takeout["status"] == "received"
    assert takeout["paid"] is False


def test_get_orders_and_not_found(client: TestClient) -> None:
    """GET /orders supports filtering and GET /orders/{id} returns 404 when missing."""
    created_t1 = client.post("/orders", json=_sample_dine_in_payload("T-01")).json()
    created_t2 = client.post("/orders", json=_sample_dine_in_payload("T-02")).json()

    all_orders = client.get("/orders").json()
    assert len(all_orders) == 2

    filtered = client.get("/orders", params={"table_id": "T-01", "status": "received"}).json()
    assert [order["order_id"] for order in filtered] == [created_t1["order_id"]]

    detail_resp = client.get(f"/orders/{created_t2['order_id']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["table_id"] == "T-02"

    missing_resp = client.get("/orders/ord_nonexistent")
    assert missing_resp.status_code == 404


def test_kanban_status_transitions(client: TestClient) -> None:
    """PATCH /orders/{id}/status enforces received -> preparing -> ready -> served."""
    order_id = client.post("/orders", json=_sample_dine_in_payload()).json()["order_id"]

    # Invalid skip: received -> ready
    skip_resp = client.patch(f"/orders/{order_id}/status", json={"status": "ready"})
    assert skip_resp.status_code == 409

    # Valid forward transitions
    for next_status in ("preparing", "ready", "served"):
        resp = client.patch(f"/orders/{order_id}/status", json={"status": next_status})
        assert resp.status_code == 200
        assert resp.json()["status"] == next_status

    # Invalid backward transition from terminal state: served -> ready
    backward_resp = client.patch(f"/orders/{order_id}/status", json={"status": "ready"})
    assert backward_resp.status_code == 409

    # Missing order
    missing_resp = client.patch("/orders/ord_missing/status", json={"status": "preparing"})
    assert missing_resp.status_code == 404


def test_table_bill_and_prevent_duplicate_payment(client: TestClient) -> None:
    """GET /tables/{id}/bill aggregates unpaid orders and mark-paid rejects duplicates."""
    order1 = client.post("/orders", json=_sample_dine_in_payload("T-10")).json()
    order2 = client.post(
        "/orders",
        json={
            "source": "dine_in",
            "table_id": "T-10",
            "items": [
                {
                    "product_id": "item-4",
                    "product_name": "Cake",
                    "unit_price": 600,
                    "quantity": 1,
                }
            ],
        },
    ).json()

    bill_before = client.get("/tables/T-10/bill")
    assert bill_before.status_code == 200
    assert bill_before.json() == {
        "table_id": "T-10",
        "order_ids": [order1["order_id"], order2["order_id"]],
        "total_amount": 3450,
    }

    # Pay first order
    pay1_resp = client.post(f"/orders/{order1['order_id']}/mark-paid")
    assert pay1_resp.status_code == 200
    assert pay1_resp.json()["paid"] is True

    # Duplicate payment returns 409
    dup_resp = client.post(f"/orders/{order1['order_id']}/mark-paid")
    assert dup_resp.status_code == 409

    # Unpaid bill now only includes order2
    bill_after = client.get("/tables/T-10/bill")
    assert bill_after.status_code == 200
    assert bill_after.json() == {
        "table_id": "T-10",
        "order_ids": [order2["order_id"]],
        "total_amount": 600,
    }

    # Missing order mark-paid returns 404
    missing_pay = client.post("/orders/ord_missing/mark-paid")
    assert missing_pay.status_code == 404


def test_order_ui_screens(client: TestClient) -> None:
    """UI screens render kanban, detail, and bills views."""
    client.post("/orders", json=_sample_dine_in_payload("T-10"))
    for path in ("/ui/orders/kanban", "/ui/orders/detail", "/ui/orders/bills"):
        res = client.get(path)
        assert res.status_code == 200
        assert "注文管理" in res.text
