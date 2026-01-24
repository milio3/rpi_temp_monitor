from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta
import os

from .database import get_session, create_db_and_tables
from .models import TemperatureReading

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/api/readings/latest", response_model=TemperatureReading)
def get_latest_reading(session: Session = Depends(get_session)):
    reading = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.desc()).limit(1)).first()
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

@app.get("/api/readings/history", response_model=List[TemperatureReading])
def get_history(days: int = 30, session: Session = Depends(get_session)):
    cutoff = datetime.now() - timedelta(days=days)
    readings = session.exec(select(TemperatureReading).where(TemperatureReading.timestamp >= cutoff).order_by(TemperatureReading.timestamp.asc())).all()
    return readings

@app.get("/api/readings/stats/monthly")
def get_monthly_stats(session: Session = Depends(get_session)):
    # Procesamiento en Python para simplificar lógica de SQLite
    readings = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.asc())).all()
    
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

@app.post("/api/readings", response_model=TemperatureReading)
def create_reading(reading: TemperatureReading, session: Session = Depends(get_session)):
    session.add(reading)
    session.commit()
    session.refresh(reading)
    return reading

from fastapi.responses import Response
import csv
import io



@app.get("/api/readings/export/csv")
def export_readings_csv(session: Session = Depends(get_session)):
    readings = session.exec(select(TemperatureReading).order_by(TemperatureReading.timestamp.desc())).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Timestamp', 'Temperature'])
    
    for r in readings:
        writer.writerow([r.id, r.timestamp, r.temperature])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rpi_readings.csv"}
    )

# Servir Frontend estático
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
