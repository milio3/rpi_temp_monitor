import csv
import io
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import text
from sqlmodel import Session, select, func

from app.core.config import settings
from app.models.reading import TemperatureReading
from app.schemas.readings import MonthlyStatItem, ThermalSummary

def _ensure_aware_utc(dt: datetime) -> datetime:
    """Asegura que un datetime sea offset-aware en UTC para comparaciones consistentes."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def get_thermal_status(temp: float) -> str:
    """Devuelve el estado semántico según los umbrales térmicos."""
    if temp >= settings.CRITICAL_TEMP:
        return "critical"
    elif temp >= settings.WARNING_TEMP:
        return "warning"
    return "normal"

def get_thermal_summary(session: Session) -> ThermalSummary:
    """Calcula el resumen consolidado de las métricas térmicas."""
    latest_reading = session.exec(
        select(TemperatureReading).order_by(TemperatureReading.timestamp.desc()).limit(1)
    ).first()

    total_readings = session.exec(select(func.count(TemperatureReading.id))).one() or 0

    if not latest_reading:
        return ThermalSummary(
            current_temp=0.0,
            current_status="normal",
            last_timestamp=datetime.now(timezone.utc),
            min_24h=0.0,
            max_24h=0.0,
            avg_24h=0.0,
            thermal_headroom=settings.THROTTLING_TEMP,
            total_readings=0,
            sensor_mode="simulado" if settings.SIMULATE_TEMP else "físico",
            check_interval_seconds=settings.CHECK_INTERVAL,
        )

    # Normalizar marca temporal
    reading_dt = _ensure_aware_utc(latest_reading.timestamp)
    now_dt = datetime.now(timezone.utc)

    # Ventana de las últimas 24 horas
    cutoff = now_dt - timedelta(hours=24)
    # Si la última lectura es anterior a 24h, tomamos las 24h previas a la última lectura
    if reading_dt < cutoff:
        cutoff = reading_dt - timedelta(hours=24)

    stats_24h = session.exec(
        select(
            func.min(TemperatureReading.temperature),
            func.max(TemperatureReading.temperature),
            func.avg(TemperatureReading.temperature),
        ).where(TemperatureReading.timestamp >= cutoff)
    ).one_or_none()

    min_24h = round(stats_24h[0], 2) if stats_24h and stats_24h[0] is not None else round(latest_reading.temperature, 2)
    max_24h = round(stats_24h[1], 2) if stats_24h and stats_24h[1] is not None else round(latest_reading.temperature, 2)
    avg_24h = round(stats_24h[2], 2) if stats_24h and stats_24h[2] is not None else round(latest_reading.temperature, 2)

    headroom = max(0.0, round(settings.THROTTLING_TEMP - latest_reading.temperature, 2))
    status = get_thermal_status(latest_reading.temperature)

    return ThermalSummary(
        current_temp=round(latest_reading.temperature, 2),
        current_status=status,
        last_timestamp=latest_reading.timestamp,
        min_24h=min_24h,
        max_24h=max_24h,
        avg_24h=avg_24h,
        thermal_headroom=headroom,
        total_readings=total_readings,
        sensor_mode="simulado" if settings.SIMULATE_TEMP else "físico",
        check_interval_seconds=settings.CHECK_INTERVAL,
    )

def _format_datetime_short(ts_val) -> str:
    """Formatea una marca temporal al formato año-mes-día hora:minuto (YYYY-MM-DD HH:MM)."""
    if not ts_val:
        return ""
    ts_str = str(ts_val).replace("T", " ").split(".")[0].strip()
    return ts_str[:16]

def get_monthly_stats(session: Session) -> List[MonthlyStatItem]:
    """Genera el desglose mensual de temperaturas mínimas, máximas y promedios con fechas."""
    query = text("""
        WITH monthly_agg AS (
            SELECT substr(timestamp, 1, 7) as mes,
                   min(temperature) as min_temp,
                   max(temperature) as max_temp,
                   avg(temperature) as avg_temp,
                   count(id) as total
            FROM temperaturereading
            GROUP BY mes
        )
        SELECT m.mes, m.min_temp, m.max_temp, round(m.avg_temp, 2), m.total,
               (SELECT timestamp FROM temperaturereading r1 WHERE substr(r1.timestamp, 1, 7) = m.mes AND r1.temperature = m.min_temp LIMIT 1) as min_time,
               (SELECT timestamp FROM temperaturereading r2 WHERE substr(r2.timestamp, 1, 7) = m.mes AND r2.temperature = m.max_temp LIMIT 1) as max_time
        FROM monthly_agg m
        ORDER BY m.mes DESC
    """)
    rows = session.exec(query).all()

    items: List[MonthlyStatItem] = []
    for row in rows:
        mes, min_temp, max_temp, avg_temp, total, min_time, max_time = row
        items.append(
            MonthlyStatItem(
                month=str(mes),
                min=round(float(min_temp), 2),
                max=round(float(max_temp), 2),
                avg=round(float(avg_temp), 2) if avg_temp is not None else round(float(min_temp), 2),
                min_time=_format_datetime_short(min_time),
                max_time=_format_datetime_short(max_time),
                count=int(total),
            )
        )
    return items

def get_history_readings(session: Session, days: int = 30) -> List[TemperatureReading]:
    """Obtiene las lecturas históricas ordenadas cronológicamente para las gráficas."""
    latest_reading = session.exec(
        select(TemperatureReading).order_by(TemperatureReading.timestamp.desc()).limit(1)
    ).first()

    if not latest_reading:
        return []

    reading_dt = _ensure_aware_utc(latest_reading.timestamp)
    now_dt = datetime.now(timezone.utc)

    cutoff = now_dt - timedelta(days=days)
    if reading_dt < cutoff:
        cutoff = reading_dt - timedelta(days=days)

    return session.exec(
        select(TemperatureReading)
        .where(TemperatureReading.timestamp >= cutoff)
        .order_by(TemperatureReading.timestamp.asc())
    ).all()

def generate_csv_content(session: Session) -> str:
    """Genera el contenido CSV completo de las lecturas registradas."""
    readings = session.exec(
        select(TemperatureReading).order_by(TemperatureReading.timestamp.desc())
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp", "Temperature"])
    for r in readings:
        writer.writerow([r.id, r.timestamp.isoformat() if isinstance(r.timestamp, datetime) else str(r.timestamp), round(r.temperature, 2)])
    return output.getvalue()
