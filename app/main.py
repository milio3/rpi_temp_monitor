import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.v1.endpoints import router as v1_router
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.services.monitor import run_periodic_monitor
from app.web.router import router as web_router

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rpi_temp_monitor")

# Evento para detención limpia de la tarea en segundo plano
stop_event = asyncio.Event()
monitor_task: asyncio.Task | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida unificado de la aplicación y el monitor térmico."""
    global monitor_task
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}...")

    # Inicialización de tablas y pragmas SQLite
    create_db_and_tables()

    # Inicio del monitor periódico en segundo plano (un solo proceso/contenedor)
    stop_event.clear()
    monitor_task = asyncio.create_task(run_periodic_monitor(stop_event))

    yield

    # Detención controlada al recibir señal de apagado
    logger.info("Apagando servicio y finalizando monitor térmico...")
    stop_event.set()
    if monitor_task:
        monitor_task.cancel()
        try:
            await asyncio.wait_for(monitor_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass
    logger.info("Servicio detenido correctamente.")

# Instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Centro de control térmico unificado para Raspberry Pi DietPi ARM64.",
    lifespan=lifespan,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (CSS, JS, favicon)
STATIC_DIR = Path(__file__).resolve().parent / "web" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    logger.warning(f"Directorio de estáticos no encontrado en {STATIC_DIR}")

# Inclusión de Routers
app.include_router(health_router)
app.include_router(v1_router, prefix=settings.API_V1_STR)
# Compatibilidad retroactiva para clientes que llamen a /api sin prefijo v1
app.include_router(v1_router, prefix="/api")
app.include_router(web_router)
