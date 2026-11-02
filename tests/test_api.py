from datetime import datetime, timezone
from starlette.testclient import TestClient

def test_get_latest_reading(client: TestClient):
    """Verifica la obtención de la última lectura registrada."""
    response = client.get("/api/v1/readings/latest")
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert data["temperature"] == 52.3

def test_get_history_readings(client: TestClient):
    """Verifica la consulta de historial cronológico."""
    response = client.get("/api/v1/readings/history?days=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["temperature"] <= data[-1]["temperature"]

def test_get_thermal_summary(client: TestClient):
    """Verifica el cálculo del resumen de métricas 24h y headroom."""
    response = client.get("/api/v1/readings/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["current_temp"] == 52.3
    assert data["min_24h"] == 42.0
    assert data["max_24h"] == 52.3
    assert data["current_status"] == "normal"
    assert data["thermal_headroom"] > 0
    assert data["total_readings"] >= 3

def test_get_monthly_stats(client: TestClient):
    """Verifica las estadísticas mensuales agregadas."""
    response = client.get("/api/v1/readings/stats/monthly")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["min"] == 42.0
    assert data[0]["max"] == 52.3

def test_create_reading(client: TestClient):
    """Verifica el registro manual de una nueva lectura."""
    payload = {
        "temperature": 55.4,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["temperature"] == 55.4
    assert "id" in data

def test_export_csv(client: TestClient):
    """Verifica la generación del archivo CSV de lecturas."""
    response = client.get("/api/v1/readings/export/csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "ID,Timestamp,Temperature" in response.text

def test_legacy_api_compatibility(client: TestClient):
    """Verifica la retrocompatibilidad de rutas en /api sin prefijo v1."""
    response = client.get("/api/readings/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 52.3
