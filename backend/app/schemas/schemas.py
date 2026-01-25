from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel

class TemperatureReadingBase(SQLModel):
    temperature: float
    timestamp: datetime

class TemperatureReadingCreate(TemperatureReadingBase):
    pass

class TemperatureReadingRead(TemperatureReadingBase):
    id: int
