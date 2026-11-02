# Plan Técnico: Arquitectura Modular Nivel 2 y Dashboard Fullstack (v4.0.0)

## 1. Arquitectura del Sistema

Se migra el proyecto a la **Estructura Canónica Modular Nivel 2** definida en `GEMINI.md`:

```text
rpi_temp_monitor/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Instancia FastAPI, lifespan con monitor en segundo plano
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings con VERSION = "4.0.0"
│   │   └── database.py          # SQLite WAL, busy_timeout=10000, foreign_keys=ON
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py            # GET /health y GET /ready
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints.py     # Endpoints REST (lecturas, estadísticas, exportación)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── readings.py          # Esquemas Pydantic para lecturas y estadísticas
│   ├── models/
│   │   ├── __init__.py
│   │   └── reading.py           # Modelo SQLModel/SQLAlchemy 'temperaturereading'
│   ├── services/
│   │   ├── __init__.py
│   │   ├── monitor.py           # Lector térmico (/sys/... o simulación) y ciclo periódico
│   │   └── stats.py             # Cálculo de métricas: 24h, mensual, headroom térmico
│   └── web/
│       ├── __init__.py
│       ├── router.py            # Vistas Jinja2 y fragmentos HTMX
│       ├── static/
│       │   ├── css/style.css    # Tokens tema oscuro WCAG 2.2 AA (Grafito/Carbón)
│       │   ├── js/dashboard.js  # Integración de Chart.js y gestión de gráficas
│       │   └── favicon.png      # Favicon corporativo del proyecto
│       └── templates/
│           ├── layouts/base.html
│           ├── pages/index.html
│           ├── components/
│           │   ├── icon.html    # Macro de iconos SVG
│           │   ├── navbar.html  # Barra superior de navegación y estado
│           │   └── kpi_card.html# Tarjeta ergonómica de métrica
│           └── fragments/
│               ├── current_temp.html   # Fragmento HTMX para auto-refresco
│               ├── stats_summary.html  # Fragmento HTMX de resumen de métricas
│               ├── monthly_table.html  # Tabla mensual con paginación/scroll
│               └── modal_history.html  # Contenido del modal histórico
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configuración de base de datos en memoria y mocks
│   ├── test_health.py           # Validación de /health y /ready
│   ├── test_api.py              # Validación de endpoints REST y exportación CSV
│   ├── test_services.py         # Pruebas del servicio térmico y estadísticas
│   └── test_web.py              # Validación de renderizado Jinja2 y fragmentos HTMX
├── .specify/
│   └── specs/001-renovacion-arquitectura-ui/
├── compose.yml                  # 1 Contenedor rpi_temp_webapp, puerto 8085:8000, 512M
├── Dockerfile                   # Python 3.12-slim, uv, appuser, sin pip
├── requirements.txt             # Dependencias fijadas para producción
└── .env.example                 # Variables de entorno documentadas
```

---

## 2. Contratos de API y Rutas Web

### Endpoints del Sistema y Salud (`app/api/health.py`)
- `GET /health`: Estado liveness. Respuesta 200: `{"status": "ok", "version": "4.0.0", "timestamp": "..."}`.
- `GET /ready`: Estado readiness. Verifica conexión activa SQLite. Respuesta 200: `{"status": "ready", "database": "connected"}` (o 503 ante fallo).

### Endpoints REST (`app/api/v1/endpoints.py`)
- `GET /api/v1/readings/latest`: Última lectura registrada (`TemperatureReadingRead`).
- `GET /api/v1/readings/history?days=30`: Listado cronológico de lecturas.
- `GET /api/v1/readings/stats/summary`: Resumen de métricas (actual, mín/máx/media 24h, margen térmico, total lecturas).
- `GET /api/v1/readings/stats/monthly`: Agrupación mensual con mínimas y máximas temporizadas.
- `GET /api/v1/readings/export/csv`: Descarga de archivo `rpi_readings.csv`.
- `POST /api/v1/readings`: Registro manual de lectura (para integración de pruebas/sensores externos).

### Rutas Web y Fragmentos HTMX (`app/web/router.py`)
- `GET /`: Vista principal completa del dashboard ergonómico.
- `GET /web/fragments/current-temp`: Fragmento HTML con la temperatura actual y badge de estado.
- `GET /web/fragments/stats-summary`: Fragmento HTML con las tarjetas KPI de 24h y headroom.
- `GET /web/fragments/monthly-table`: Fragmento HTML con la tabla de meses anteriores.
- `GET /web/fragments/modal-history`: Fragmento HTML con la tabla detallada del modal.

---

## 3. Infraestructura y Despliegue en 1 Único Contenedor

1. **Gestión del Monitor:** Dentro de `app/main.py`, la función de ciclo de vida `lifespan` lanza una tarea `asyncio.create_task(run_periodic_monitor())`. De esta forma:
   - No se necesitan dos contenedores en Docker.
   - Desaparece cualquier conflicto de bloqueo sobre el archivo SQLite.
   - El consumo de memoria y CPU en la Raspberry Pi se reduce a la mitad.
2. **`compose.yml`:**
   - Un solo servicio `rpi_temp_webapp`.
   - Contenedor con reinicio `unless-stopped`.
   - Límite de memoria fijado a `512M`.
   - Puerto `8085:8000`.
   - Montura de persistencia `/mnt/dietpi_userdata/apps/rpi_temp_monitor/data:/app/data` (y mapeo `./data:/app/data` para desarrollo local).
   - Montura de solo lectura `/sys:/sys:ro` para acceso a los sensores térmicos reales en la Raspberry Pi.
3. **`Dockerfile`:**
   - Base `python:3.12-slim`.
   - Instalación mediante `uv` oficial binario (`ghcr.io/astral-sh/uv:latest`).
   - Creación de usuario sin privilegios `appuser` (UID 1000).
   - Ejecución sin buffer de logs (`PYTHONUNBUFFERED=1`).

---

## 4. Estrategia de Pruebas y Validación Dual

- **Aislamiento absoluto:** `tests/conftest.py` utiliza `sqlite:///:memory:` y anula `get_session` para que ninguna prueba acceda o altere la base de datos real.
- **Matriz Dual:**
  - Python 3.15: `uv run --python 3.15 pytest -v`
  - Python 3.12: `uv run --python 3.12 pytest -v`
