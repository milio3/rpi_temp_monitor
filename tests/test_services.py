from sqlmodel import Session
from app.services.monitor import get_cpu_temp, record_current_temperature
from app.services.stats import get_thermal_status, get_thermal_summary

def test_get_thermal_status_thresholds():
    """Verifica los umbrales semánticos de temperatura."""
    assert get_thermal_status(45.0) == "normal"
    assert get_thermal_status(59.9) == "normal"
    assert get_thermal_status(60.0) == "warning"
    assert get_thermal_status(74.9) == "warning"
    assert get_thermal_status(75.0) == "critical"
    assert get_thermal_status(85.0) == "critical"

def test_cpu_temp_reading_or_simulation():
    """Verifica que get_cpu_temp retorna un valor float válido."""
    temp = get_cpu_temp()
    assert temp is not None
    assert isinstance(temp, float)
    assert 20.0 <= temp <= 95.0

def test_record_current_temperature_persists(session: Session):
    """Verifica la persistencia de una lectura mediante record_current_temperature."""
    initial_summary = get_thermal_summary(session)
    initial_count = initial_summary.total_readings

    reading = record_current_temperature(session=session)
    assert reading is not None
    assert reading.id is not None
    assert reading.temperature > 0

    after_summary = get_thermal_summary(session)
    assert after_summary.total_readings == initial_count + 1
