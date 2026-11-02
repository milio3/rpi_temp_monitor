# 🌡️ RPi Temp Monitor (v4.0.0)

Sistema integral de monitorización y observabilidad térmica para Raspberry Pi (DietPi OS ARM64) y entornos de desarrollo, construido con **FastAPI**, **SQLite en modo WAL**, **Docker Compose** y una interfaz ergonómica en **modo oscuro** (WCAG 2.2 AA) impulsada por **Jinja2**, **HTMX**, **Alpine.js** y **Tailwind CSS**.

---

## 🚀 Novedades de la Versión 4.0.0

- **🐳 Arquitectura Consolidada en 1 Contenedor:** Eliminación del contenedor separado de monitoreo. FastAPI gestiona ahora tanto la API y la interfaz web como la captura periódica de temperatura mediante una tarea asíncrona unificada en su ciclo de vida (`lifespan`).
- **🖥️ Dashboard Ergonómico Dark (WCAG 2.2 AA):**
  - Paleta en grafito y carbón (`#171A1F`, `#20252C`, `#282F38`) sin negros puros agresivos.
  - Diseñado específicamente para monitores QHD de 32" con tipografía funcional >= 15 px (evitando fatiga visual).
  - Componentes reactivos declarativos con **HTMX** (auto-refresco sin recargas completas ni parpadeos).
  - Estado de modales accesible y desacoplado mediante **Alpine.js** (sin peticiones fetch en el cliente).
  - Iconografía 100% SVG vectorial (cero emojis decorativos).
- **📊 Mayor Riqueza de Información Térmica:**
  - KPI de temperatura actual con semántica de estado (*Óptimo* < 60°C, *Aviso* 60-75°C, *Crítico* > 75°C).
  - Cálculo de **Margen Térmico** (*Thermal Headroom*) respecto al límite de estrangulamiento térmico de la Raspberry Pi (80 °C).
  - Resumen de 24 horas: Mínima, Máxima y Promedio diario.
  - Histórico mensual consolidado con marcas temporales exactas de mínimas y máximas.
  - Gráficas interactivas optimizadas para tema oscuro: actividad 24h y tendencia 30 días.
  - Exportación de todo el historial a formato CSV descargable.
- **🛡️ Cumplimiento Normativo y Seguridad:**
  - SQLite configurado en modo WAL con `busy_timeout=10000`, `synchronous=NORMAL` y `foreign_keys=ON`.
  - Endpoints canónicos de observabilidad `GET /health` (liveness) y `GET /ready` (readiness).
  - `Dockerfile` hardened con usuario sin privilegios `appuser` (UID 1000) e instalador ultrarrápido `uv`.
  - `compose.yml` con límites estrictos de recursos (`memory: 512M`) y healthcheck automatizado.
  - Suite de pruebas con aislamiento estricto en memoria validada en **Python 3.12** y **Python 3.15**.

---

## 📂 Estructura Canónica del Proyecto (Modular Nivel 2)

```text
rpi_temp_monitor/
├── app/
│   ├── main.py                  # Instancia FastAPI, lifespan con monitor térmico
│   ├── core/
│   │   ├── config.py            # Configuración tipada con Pydantic Settings
│   │   └── database.py          # Conexión SQLite WAL y sesiones
│   ├── api/
│   │   ├── health.py            # Endpoints GET /health y GET /ready
│   │   └── v1/
│   │       └── endpoints.py     # Endpoints REST (lecturas, estadísticas, CSV)
│   ├── schemas/
│   │   └── readings.py          # Esquemas Pydantic (DTO de entrada y salida)
│   ├── models/
│   │   └── reading.py           # Modelo SQLModel 'temperaturereading'
│   ├── services/
│   │   ├── monitor.py           # Lector de sensor (/sys/... o simulado) y ciclo
│   │   └── stats.py             # Agregación mensual, 24h y margen térmico
│   └── web/
│       ├── router.py            # Rutas Jinja2 y fragmentos HTMX
│       ├── static/              # CSS de tema oscuro, JS Chart.js y favicon
│       └── templates/           # Plantillas: layouts, pages, components, fragments
├── tests/                       # Pruebas automatizadas con BD aislada
├── .specify/                    # Especificaciones funcionales y planes SDD
├── compose.yml                  # Orquestación con 1 contenedor y límites
├── Dockerfile                   # Imagen hardened ARM64/Python 3.12 con uv
├── requirements.txt             # Dependencias de producción fijadas
└── README.md
```

---

## 🛠️ Despliegue en Producción (Raspberry Pi DietPi)

El puerto asignado canónicamente en el host de producción es el **8085**:

| Parámetro | Valor Canónico |
| :--- | :--- |
| **Servidor / Arquitectura** | Raspberry Pi (DietPi OS, ARM64) |
| **IP de Producción** | `192.168.1.33` |
| **Puerto Host** | `8085` |
| **URL de Acceso** | `http://192.168.1.33:8085` |
| **Contenedor** | `rpi_temp_webapp` |
| **Ruta de Datos Persistentes** | `/mnt/dietpi_userdata/apps/rpi_temp_monitor/data` |

### Despliegue con Docker Compose

```bash
# Construir y levantar el contenedor en segundo plano
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f webapp
```

---

## 💻 Desarrollo Local (PC Windows / Linux)

El sistema detecta automáticamente si se encuentra en Windows o si el sensor de hardware no está presente, activando el modo de simulación térmica sin requerir cambios de configuración.

1. **Crear entorno e instalar dependencias con `uv`**:
   ```bash
   uv venv --python 3.12
   uv pip install -r requirements.txt pytest httpx
   ```

2. **Ejecutar servidor**:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```
   Accede a la interfaz web en `http://localhost:8000` y a la documentación interactiva OpenAPI en `http://localhost:8000/docs`.

3. **Ejecutar Pruebas Automatizadas**:
   ```bash
   uv run pytest -v
   ```

---

## 📝 Historial de Versiones

### v4.0.0 (2026-11-02) — Arquitectura Unificada & UI Dark Dashboard
- Unificación en un único contenedor Docker (`rpi_temp_webapp`) con monitor térmico asíncrono en lifespan.
- Rediseño ergonómico de la web según estándar `ui-dark-dashboard` (FastAPI + Jinja2 + HTMX + Alpine.js + Tailwind CSS).
- Nuevas métricas: Margen térmico hasta 80 °C, resumen 24h, histórico mensual temporizado y descarga CSV.
- Integración de `GET /health` y `GET /ready`.
- Pruebas automatizadas aprobadas en matriz dual Python 3.12 y 3.15.
- Construcción optimizada con `uv` y límites de memoria a 512M en `compose.yml`.

### v3.1.0 (2026-01-25)
- Ajustes de legibilidad en ejes de gráficas y formato de fechas.

### v3.0.0 (2026-01-25)
- Modularización inicial del backend con FastAPI y SQLModel.
