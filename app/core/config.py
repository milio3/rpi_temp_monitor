import os
import platform
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación."""

    PROJECT_NAME: str = "RPi Temp Monitor"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "production"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Persistencia SQLite
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_URL: str = ""

    # Monitorización térmica
    CHECK_INTERVAL: int = 600  # 10 minutos
    TEMP_SENSOR_PATH: str = "/sys/class/thermal/thermal_zone0/temp"
    SIMULATE_TEMP: bool = False
    WARNING_TEMP: float = 60.0
    CRITICAL_TEMP: float = 75.0
    THROTTLING_TEMP: float = 80.0

    # Localización y Timeouts
    TIMEZONE: str = "Europe/Madrid"
    HTTP_TIMEOUT_SECONDS: float = 10.0

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Asegurar directorio de datos
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Resolver DATABASE_URL por defecto si no está provista
        if not self.DATABASE_URL:
            db_path = self.DATA_DIR / "database.db"
            # Si aún no existe en data/ pero existe en backend/database.db, usar el de backend temporalmente
            legacy_backend_db = self.BASE_DIR / "backend" / "database.db"
            if not db_path.exists() and legacy_backend_db.exists():
                self.DATABASE_URL = f"sqlite:///{legacy_backend_db.as_posix()}"
            else:
                self.DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

        # Configuración automática de simulación si se detecta Windows o ausencia de sensor
        is_windows = platform.system() == "Windows"
        sensor_exists = os.path.exists(self.TEMP_SENSOR_PATH)
        if is_windows or not sensor_exists:
            self.SIMULATE_TEMP = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
