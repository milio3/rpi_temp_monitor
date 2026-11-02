from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.core.config import settings
from app.core.database import get_session
from app.models.reading import TemperatureReading
from app.schemas.readings import HealthResponse, ReadyResponse

router = APIRouter(tags=["Salud y Control"])

@router.get("/health", response_model=HealthResponse, summary="Verificación de vitalidad (Liveness)")
def health_check() -> HealthResponse:
    """Retorna el estado de vitalidad de la aplicación y la versión activa."""
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
    )

@router.get("/ready", response_model=ReadyResponse, summary="Verificación de preparación (Readiness)")
def readiness_check(session: Session = Depends(get_session)) -> ReadyResponse:
    """Verifica que la conexión a la base de datos SQLite esté activa y operativa."""
    try:
        count = session.exec(select(func.count(TemperatureReading.id))).one()
        return ReadyResponse(
            status="ready",
            database="connected",
            total_readings=count or 0,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de datos no disponible: {str(e)}",
        )
