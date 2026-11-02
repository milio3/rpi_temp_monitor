from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.reading import TemperatureReading
from app.schemas.readings import (
    TemperatureReadingCreate,
    TemperatureReadingRead,
    ThermalSummary,
    MonthlyStatItem,
)
from app.services.stats import (
    get_thermal_summary,
    get_monthly_stats,
    get_history_readings,
    generate_csv_content,
)

router = APIRouter(tags=["Lecturas Térmicas"])

@router.get("/readings/latest", response_model=TemperatureReadingRead, summary="Obtener última lectura")
def get_latest_reading(session: Session = Depends(get_session)) -> TemperatureReading:
    """Retorna la lectura térmica más reciente registrada en la base de datos."""
    reading = session.exec(
        select(TemperatureReading).order_by(TemperatureReading.timestamp.desc()).limit(1)
    ).first()
    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron lecturas registradas.",
        )
    return reading

@router.get("/readings/history", response_model=List[TemperatureReadingRead], summary="Historial cronológico")
def get_history(
    days: int = Query(30, ge=1, le=365, description="Número de días de histórico a consultar"),
    session: Session = Depends(get_session),
) -> List[TemperatureReading]:
    """Retorna el listado ordenado de lecturas para representación gráfica."""
    return get_history_readings(session=session, days=days)

@router.get("/readings/stats/summary", response_model=ThermalSummary, summary="Resumen térmico consolidado")
def get_summary(session: Session = Depends(get_session)) -> ThermalSummary:
    """Retorna métricas clave: temperatura actual, mín/máx/media 24h, margen térmico y total."""
    return get_thermal_summary(session=session)

@router.get("/readings/stats/monthly", response_model=List[MonthlyStatItem], summary="Estadísticas mensuales")
def get_monthly(session: Session = Depends(get_session)) -> List[MonthlyStatItem]:
    """Retorna agregados mensuales con mínimas y máximas históricas y marcas temporales."""
    return get_monthly_stats(session=session)

@router.post("/readings", response_model=TemperatureReadingRead, status_code=status.HTTP_201_CREATED, summary="Registrar lectura")
def create_reading(
    reading_in: TemperatureReadingCreate,
    session: Session = Depends(get_session),
) -> TemperatureReading:
    """Registra manualmente una lectura de temperatura."""
    timestamp = reading_in.timestamp or datetime.now(timezone.utc)
    reading = TemperatureReading(temperature=reading_in.temperature, timestamp=timestamp)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

@router.get("/readings/export/csv", summary="Exportar lecturas a CSV")
def export_readings_csv(session: Session = Depends(get_session)) -> Response:
    """Genera y descarga un archivo CSV con todas las lecturas registradas."""
    csv_data = generate_csv_content(session=session)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rpi_readings.csv"},
    )
