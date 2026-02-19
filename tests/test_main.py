import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import store


@pytest.fixture(autouse=True)
def clear_store():
    """Reset in-memory store before every test — ensures test isolation."""
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Health ────────────────────────────────────────────────
class TestHealth:
    def test_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_response_shape(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "total_calculations" in data

    def test_reflects_store_count(self, client):
        client.post("/calculate", json={"operation": "add", "a": 1, "b": 2})
        data = client.get("/health").json()
        assert data["total_calculations"] == 1


# ── Calculate ─────────────────────────────────────────────
class TestCalculate:
    def test_add(self, client):
        response = client.post("/calculate", json={"operation": "add", "a": 5, "b": 3})
        assert response.status_code == 201
        assert response.json()["result"] == 8.0

    def test_subtract(self, client):
        response = client.post("/calculate", json={"operation": "subtract", "a": 10, "b": 4})
        assert response.json()["result"] == 6.0

    def test_multiply(self, client):
        response = client.post("/calculate", json={"operation": "multiply", "a": 3, "b": 4})
        assert response.json()["result"] == 12.0

    def test_divide(self, client):
        response = client.post("/calculate", json={"operation": "divide", "a": 10, "b": 2})
        assert response.json()["result"] == 5.0

    def test_power(self, client):
        response = client.post("/calculate", json={"operation": "power", "a": 2, "b": 3})
        assert response.json()["result"] == 8.0

    def test_modulo(self, client):
        response = client.post("/calculate", json={"operation": "modulo", "a": 10, "b": 3})
        assert response.json()["result"] == 1.0

    def test_response_has_id(self, client):
        data = client.post("/calculate", json={"operation": "add", "a": 1, "b": 1}).json()
        assert "id" in data
        assert len(data["id"]) == 36  # UUID format

    def test_response_has_timestamp(self, client):
        data = client.post("/calculate", json={"operation": "add", "a": 1, "b": 1}).json()
        assert "timestamp" in data

    # ── Validation errors ─────────────────────────────────
    def test_invalid_operation(self, client):
        response = client.post("/calculate", json={"operation": "sqrt", "a": 9, "b": 0})
        assert response.status_code == 422   # Pydantic validation error

    def test_divide_by_zero(self, client):
        response = client.post("/calculate", json={"operation": "divide", "a": 5, "b": 0})
        assert response.status_code == 400
        assert "zero" in response.json()["detail"].lower()

    def test_modulo_by_zero(self, client):
        response = client.post("/calculate", json={"operation": "modulo", "a": 5, "b": 0})
        assert response.status_code == 400

    def test_missing_field(self, client):
        response = client.post("/calculate", json={"operation": "add", "a": 1})
        assert response.status_code == 422

    def test_non_numeric_input(self, client):
        response = client.post("/calculate", json={"operation": "add", "a": "x", "b": 1})
        assert response.status_code == 422


# ── History ───────────────────────────────────────────────
class TestHistory:
    def test_empty_history(self, client):
        data = client.get("/history").json()
        assert data["total"] == 0
        assert data["records"] == []

    def test_history_grows(self, client):
        client.post("/calculate", json={"operation": "add", "a": 1, "b": 1})
        client.post("/calculate", json={"operation": "multiply", "a": 2, "b": 3})
        data = client.get("/history").json()
        assert data["total"] == 2
        assert len(data["records"]) == 2

    def test_most_recent_first(self, client):
        client.post("/calculate", json={"operation": "add", "a": 1, "b": 1})
        client.post("/calculate", json={"operation": "multiply", "a": 2, "b": 3})
        records = client.get("/history").json()["records"]
        # Most recent (multiply) should be first
        assert records[0]["operation"] == "multiply"

    def test_get_by_id(self, client):
        created = client.post("/calculate", json={"operation": "add", "a": 4, "b": 6}).json()
        fetched = client.get(f"/history/{created['id']}").json()
        assert fetched["id"] == created["id"]
        assert fetched["result"] == 10.0

    def test_get_by_invalid_id(self, client):
        response = client.get("/history/nonexistent-id")
        assert response.status_code == 404

    def test_clear_history(self, client):
        client.post("/calculate", json={"operation": "add", "a": 1, "b": 1})
        client.delete("/history")
        data = client.get("/history").json()
        assert data["total"] == 0

    def test_clear_returns_204(self, client):
        response = client.delete("/history")
        assert response.status_code == 204


# ── Metrics ───────────────────────────────────────────────
class TestMetrics:
    def test_metrics_endpoint_exists(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_contains_http_data(self, client):
        client.get("/health")   # generate some traffic first
        response = client.get("/metrics")
        assert "http_requests_total" in response.text
