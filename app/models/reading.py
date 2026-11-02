from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class TemperatureReading(SQLModel, table=True):
    """Modelo de lectura térmica compatible con la tabla histórica 'temperaturereading'."""

    __tablename__ = "temperaturereading"

    id: Optional[int] = Field(default=None, primary_key=True)
    temperature: float = Field(nullable=False)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
