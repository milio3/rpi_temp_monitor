"""Módulo de endpoints de la API."""
from app.api.health import router as health_router
from app.api.v1.endpoints import router as v1_router

__all__ = ["health_router", "v1_router"]
