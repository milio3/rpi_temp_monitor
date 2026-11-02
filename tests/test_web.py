from starlette.testclient import TestClient

def test_index_page_rendered(client: TestClient):
    """Verifica que la página principal renderiza la vista completa con HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RPi Temp Monitor" in response.text
    assert "Temperatura CPU Actual" in response.text
    assert "dailyChart" in response.text
    assert "historyChart" in response.text

def test_fragment_current_temp(client: TestClient):
    """Verifica el fragmento HTMX de temperatura actual."""
    response = client.get("/web/fragments/current-temp")
    assert response.status_code == 200
    assert "current-temp-container" in response.text
    assert "Margen hasta Throttling" in response.text

def test_fragment_stats_summary(client: TestClient):
    """Verifica el fragmento HTMX de resumen de estadísticas 24h."""
    response = client.get("/web/fragments/stats-summary")
    assert response.status_code == 200
    assert "stats-summary-container" in response.text
    assert "Mínima (24h)" in response.text
    assert "Máxima (24h)" in response.text

def test_fragment_monthly_table(client: TestClient):
    """Verifica el fragmento HTMX de la tabla mensual."""
    response = client.get("/web/fragments/monthly-table")
    assert response.status_code == 200
    assert "monthly-table-container" in response.text

def test_fragment_modal_history(client: TestClient):
    """Verifica el fragmento HTMX del modal histórico completo."""
    response = client.get("/web/fragments/modal-history")
    assert response.status_code == 200
    assert "Histórico Mensual Completo" in response.text
    assert "Descargar CSV" in response.text
