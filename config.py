"""
Configuración centralizada para el monitor de temperatura
"""
from pathlib import Path
import platform

# Rutas
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "temp.log"
TEMPLATE_FILE = BASE_DIR / "template.html"
INDEX_FILE = BASE_DIR / "index.html"
ALERT_LOG_FILE = BASE_DIR / "alerts.log"

# Configuración de simulación
IS_WINDOWS = platform.system() == "Windows"
SIMULATE_TEMP = IS_WINDOWS  # Simular si estamos en Windows

# Configuración de temperatura
TEMP_SENSOR_PATH = "/sys/class/thermal/thermal_zone0/temp"
TEMP_MIN_VALID = 0.0  # Temperatura mínima válida en °C
TEMP_MAX_VALID = 100.0  # Temperatura máxima válida en °C

# Umbrales de alerta
TEMP_WARNING_THRESHOLD = 70.0  # Warning a partir de 70°C
TEMP_CRITICAL_THRESHOLD = 80.0  # Critical a partir de 80°C

# Configuración de datos
DAILY_HOURS = 24  # Horas de datos diarios a mostrar
HISTORY_DAYS = 30  # Días de historial a mostrar
