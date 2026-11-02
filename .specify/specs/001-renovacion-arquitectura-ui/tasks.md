# Tareas de Implementación: Renovación de Arquitectura e Interfaz (v4.0.0)

- [x] **[T001]** Crear estructura canónica base, configuración Pydantic Settings con `VERSION = "4.0.0"` y conexión SQLite WAL (`app/core/config.py`, `app/core/database.py`).
- [ ] **[T002]** Definir modelos SQLModel compatibles con `temperaturereading` y esquemas Pydantic (`app/models/reading.py`, `app/schemas/readings.py`).
- [ ] **[T003]** Implementar servicios de monitorización periódica de CPU y cálculo de métricas agregadas (`app/services/monitor.py`, `app/services/stats.py`).
- [ ] **[T004]** Implementar endpoints de salud `GET /health` y `GET /ready` en `app/api/health.py` y endpoints REST v1 en `app/api/v1/endpoints.py`.
- [ ] **[T005]** Construir vistas Jinja2, macros SVG y fragmentos HTMX ergonómicos para modo oscuro WCAG 2.2 AA (`app/web/...`).
- [ ] **[T006]** Integrar aplicación principal FastAPI con ciclo de vida `lifespan` unificado y router web (`app/main.py`).
- [ ] **[T007]** Configurar suite de pruebas completa con aislamiento de base de datos en `tests/` y validar en Python 3.15 y Python 3.12.
- [ ] **[T008]** Actualizar infraestructura: `Dockerfile` con `uv`, `compose.yml` a 1 solo contenedor con límites de recursos, `requirements.txt` y `.env.example`.
- [ ] **[T009]** Preservar datos persistentes (`data/database.db`), limpiar código obsoleto redundante y actualizar documentación `README.md`.
- [ ] **[T010]** Crear tag de versión Git `v4.0.0` y verificar estado limpio del repositorio.
