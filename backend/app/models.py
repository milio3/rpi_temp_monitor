from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class TemperatureReading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    temperature: float
    timestamp: datetime = Field(default_factory=datetime.now, index=True)
