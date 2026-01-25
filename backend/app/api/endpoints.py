from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import List

from app.database import get_session
from app.models import TemperatureReading
from app.schemas import schemas

import csv
import io

router = APIRouter()

# --- Helper Functions ---

def _calculate_monthly_stats(readings: List[TemperatureReading]) -> List[dict]:
    """Procesa las lecturas para generar estadísticas mensuales."""
    stats = {}
    for r in readings:
        month = r.timestamp.strftime("%Y-%m")
        if month not in stats:
            stats[month] = {
                "min": r.temperature, "max": r.temperature,
                "min_time": r.timestamp, "max_time": r.timestamp
            }
        else:
            if r.temperature < stats[month]["min"]:
                stats[month]["min"] = r.temperature
                stats[month]["min_time"] = r.timestamp
            if r.temperature > stats[month]["max"]:
                stats[month]["max"] = r.temperature
                stats[month]["max_time"] = r.timestamp
    
    result = []
    for month, data in stats.items():
        result.append({
            "month": month,
            "min": data["min"],
            "max": data["max"],
            "min_time": data["min_time"].isoformat(),
            "max_time": data["max_time"].isoformat()
        })
    return result

def _generate_csv_content(readings: List[TemperatureReading]) -> str:
    """Genera el contenido CSV de las lecturas."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Temperature'])
    for r in readings:
        writer.writerow([r.id, r.timestamp, r.temperature])
    return output.getvalue()

# --- Routes ---

@router.get("/readings/latest", response_model=TemperatureReading)
def get_latest_reading(session: Session = Depends(get_session)):
    reading = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.desc()).limit(1)).first()
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

@router.get("/readings/history", response_model=List[TemperatureReading])
def get_history(days: int = 30, session: Session = Depends(get_session)):
    cutoff = datetime.now() - timedelta(days=days)
    readings = session.exec(select(TemperatureReading).where(TemperatureReading.timestamp >= cutoff).order_by(TemperatureReading.timestamp.asc())).all()
    return readings

@router.get("/readings/stats/monthly")
def get_monthly_stats(session: Session = Depends(get_session)):
    # Procesamiento en Python para simplificar lógica de SQLite
    readings = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.asc())).all()
    return _calculate_monthly_stats(readings)

@router.post("/readings", response_model=TemperatureReading)
def create_reading(reading: TemperatureReading, session: Session = Depends(get_session)):
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

@router.get("/readings/export/csv")
def export_readings_csv(session: Session = Depends(get_session)):
    readings = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.desc())).all()
    csv_content = _generate_csv_content(readings)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rpi_readings.csv"}
    )
