from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TemperatureReadingBase(BaseModel):
    """Esquema base para lectura térmica."""
    temperature: float = Field(..., description="Temperatura en grados Celsius")
    timestamp: datetime = Field(..., description="Fecha y hora de la lectura")

class TemperatureReadingCreate(BaseModel):
    """Esquema para creación de nueva lectura."""
    temperature: float = Field(..., description="Temperatura en grados Celsius")
    timestamp: Optional[datetime] = Field(None, description="Fecha y hora opcional (por defecto ahora)")

class TemperatureReadingRead(TemperatureReadingBase):
    """Esquema de salida para lecturas persistidas."""
    id: int = Field(..., description="Identificador único")

    model_config = ConfigDict(from_attributes=True)

class MonthlyStatItem(BaseModel):
    """Estadísticas agrupadas por mes."""
    month: str = Field(..., description="Mes en formato YYYY-MM")
    min: float = Field(..., description="Temperatura mínima registrada")
    max: float = Field(..., description="Temperatura máxima registrada")
    avg: float = Field(..., description="Temperatura promedio")
    min_time: str = Field(..., description="Fecha y hora de la temperatura mínima")
    max_time: str = Field(..., description="Fecha y hora de la temperatura máxima")
    count: int = Field(..., description="Cantidad total de lecturas en el mes")

class ThermalSummary(BaseModel):
    """Resumen consolidado del estado térmico del sistema."""
    current_temp: float = Field(..., description="Temperatura actual en °C")
    current_status: str = Field(..., description="Estado: normal, warning o critical")
    last_timestamp: datetime = Field(..., description="Marca temporal de la última lectura")
    min_24h: float = Field(..., description="Temperatura mínima en las últimas 24 horas")
    max_24h: float = Field(..., description="Temperatura máxima en las últimas 24 horas")
    avg_24h: float = Field(..., description="Temperatura media en las últimas 24 horas")
    thermal_headroom: float = Field(..., description="Margen térmico hasta límite de throttling (80°C)")
    total_readings: int = Field(..., description="Total histórico de lecturas almacenadas")
    sensor_mode: str = Field(..., description="Origen de datos: físico o simulado")
    check_interval_seconds: int = Field(..., description="Intervalo entre lecturas en segundos")

class HealthResponse(BaseModel):
    """Respuesta de liveness."""
    status: str = "ok"
    version: str
    timestamp: datetime

class ReadyResponse(BaseModel):
    """Respuesta de readiness."""
    status: str = "ready"
    database: str = "connected"
    total_readings: int
