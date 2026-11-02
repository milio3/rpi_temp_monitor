import asyncio
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlmodel import Session
from app.core.config import settings
from app.core.database import engine
from app.models.reading import TemperatureReading

logger = logging.getLogger(__name__)

def get_cpu_temp() -> Optional[float]:
    """Obtiene la temperatura de la CPU desde el sensor del sistema o mediante simulación."""
    if settings.SIMULATE_TEMP:
        return round(random.uniform(41.5, 53.5), 2)

    sensor_path = Path(settings.TEMP_SENSOR_PATH)
    try:
        if sensor_path.exists():
            with open(sensor_path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                return round(float(raw) / 1000.0, 2)
        else:
            logger.warning(f"Sensor térmico no encontrado en {sensor_path}. Activando simulación.")
            return round(random.uniform(42.0, 52.0), 2)
    except Exception as e:
        logger.error(f"Error leyendo sensor térmico {sensor_path}: {e}")
        return None

def record_current_temperature(session: Optional[Session] = None) -> Optional[TemperatureReading]:
    """Captura y persiste la lectura térmica actual en la base de datos."""
    temp = get_cpu_temp()
    if temp is None:
        logger.warning("No se pudo obtener la temperatura para registrar.")
        return None

    reading = TemperatureReading(temperature=temp, timestamp=datetime.now(timezone.utc))

    if session is not None:
        session.add(reading)
        session.commit()
        session.refresh(reading)
        return reading

    with Session(engine) as auto_session:
        auto_session.add(reading)
        auto_session.commit()
        auto_session.refresh(reading)
        return reading

async def run_periodic_monitor(stop_event: Optional[asyncio.Event] = None) -> None:
    """Tarea asíncrona que monitoriza periódicamente la temperatura en segundo plano."""
    logger.info(f"Iniciando monitor térmico unificado (Intervalo: {settings.CHECK_INTERVAL}s)...")

    # Lectura inicial inmediata al arrancar el contenedor
    try:
        record_current_temperature()
    except Exception as e:
        logger.error(f"Error en lectura térmica inicial: {e}")

    while True:
        if stop_event and stop_event.is_set():
            logger.info("Detención del monitor térmico solicitada.")
            break

        try:
            await asyncio.sleep(settings.CHECK_INTERVAL)
            if stop_event and stop_event.is_set():
                break
            record_current_temperature()
        except asyncio.CancelledError:
            logger.info("Tarea de monitor térmico cancelada.")
            break
        except Exception as e:
            logger.error(f"Error en ciclo de monitorización térmica: {e}")
