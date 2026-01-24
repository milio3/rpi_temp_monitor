import time
import random
import logging
import platform
from datetime import datetime
from sqlmodel import Session
from app.database import engine
from app.models import TemperatureReading
from app.database import create_db_and_tables

# Configuración básica (Hardcoded para simplificar o mover config.py aquí)
IS_WINDOWS = platform.system() == "Windows"
SIMULATE_TEMP = IS_WINDOWS
TEMP_SENSOR_PATH = "/sys/class/thermal/thermal_zone0/temp"
CHECK_INTERVAL = 600 # segundos (10 minutos)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_cpu_temp():
    if SIMULATE_TEMP:
        return random.uniform(40.0, 60.0)
    
    try:
        with open(TEMP_SENSOR_PATH, "r") as f:
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
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
