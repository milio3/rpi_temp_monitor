import os
import platform
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RPi Temp Monitor"
    API_V1_STR: str = "/api"
    
    # Database
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    
    # Monitor settings
    CHECK_INTERVAL: int = 600  # 10 minutes
    IS_WINDOWS: bool = platform.system() == "Windows"
    SIMULATE_TEMP: bool = IS_WINDOWS
    TEMP_SENSOR_PATH: str = "/sys/class/thermal/thermal_zone0/temp"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        case_sensitive = True

settings = Settings()
