from starlette.testclient import TestClient

def test_health_liveness(client: TestClient):
    """Verifica que el endpoint GET /health responde con estado OK y versión correcta."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "4.0.0"
    assert "timestamp" in data

def test_ready_readiness(client: TestClient):
    """Verifica que el endpoint GET /ready valida la conexión a SQLite."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["total_readings"] >= 3
