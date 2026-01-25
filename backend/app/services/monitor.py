import time
import random
import logging
from datetime import datetime
from sqlmodel import Session
from app.database import engine, create_db_and_tables
from app.models import TemperatureReading
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cpu_temp():
    if settings.SIMULATE_TEMP:
        return random.uniform(40.0, 60.0)
    
    try:
        with open(settings.TEMP_SENSOR_PATH, "r") as f:
            raw = f.read().strip()
            return float(raw) / 1000.0
    except Exception as e:
        logging.error(f"Error leyendo sensor: {e}")
        return None

def main():
    logging.info("Iniciando servicio de monitoreo...")
    create_db_and_tables()
    
    while True:
        try:
            temp = get_cpu_temp()
            if temp is not None:
                reading = TemperatureReading(temperature=temp, timestamp=datetime.now())
                with Session(engine) as session:
                    session.add(reading)
                    session.commit()
                logging.info(f"Lectura guardada: {temp:.2f}°C")
            else:
                logging.warning("No se pudo obtener lectura de temperatura.")
        except Exception as e:
            logging.error(f"Error en el ciclo de monitoreo: {e}")
        
        time.sleep(settings.CHECK_INTERVAL)

if __name__ == "__main__":
    main()
