# 🌡️ Monitor de Temperatura - Raspberry Pi (v3.1)

Sistema de monitoreo profesional de temperatura para Raspberry Pi utilizando **FastAPI**, **SQLite**, **Docker** y una **SPA** moderna.

## ✨ Características

-   **🏗️ Arquitectura Modular**: Backend FastAPI reestructurado siguiendo principios SOLID.
-   **🐳 Despliegue Docker**: Contenedorizado y optimizado para Portainer.
-   **💾 Base de Datos SQLite**: Almacenamiento eficiente de lecturas históricas.
-   **📊 Visualización Avanzada**:
    -   Gráfico de actividad 24h.
    -   Histórico de 15 días con máximas y mínimas.
    -   Modal de estadísticas mensuales/anuales.
-   **🛡️ Resilient**: Servicio de monitoreo independiente que persiste datos ante caídas del servidor web.
-   **⚡ Interfaz Reactiva**: Actualización en tiempo real sin recargas de página.

## 📂 Estructura del Proyecto

```
rpi_temp_monitor/
├── backend/
│   ├── app/
│   │   ├── api/            # Endpoints API (Routers)
│   │   ├── core/           # Configuración (Pydantic Settings)
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio (Monitor)
│   │   ├── main.py         # Entrypoint
│   │   └── database.py     # Session Manager
│   └── requirements.txt
├── frontend/               # Single Page Application
├── scripts/                # Scripts de utilidad (migraciones, etc)
├── docs/                   # Guías de despliegue
├── docker-compose.yml      # Orquestación de contenedores
└── Dockerfile              # Definición de imagen
```

## 🚀 Instalación y Despliegue

### Opción Recomendada: Docker / Portainer

Sigue la guía detallada en [docs/GUIA_RPI.md](docs/GUIA_RPI.md).

### Desarrollo Local (sin Docker)

1.  **Instalar dependencias**:
    ```bash
    pip install -r backend/requirements.txt
    ```

2.  **Ejecutar Backend**:
    ```bash
    cd backend
    python -m uvicorn app.main:app --reload
    ```

3.  **Ejecutar Servicio de Monitoreo** (Simulado en Windows):
    ```bash
    cd backend
    python -m app.services.monitor
    ```

## 📝 Changelog

### v3.1.0 (2026-01-25) - UI Polish Update 🎨
-   **📊 Gráficas Mejoradas**:
    -   Aumento de legibilidad en ejes (fuentes más grandes y mayor contraste).
    -   Optimización de escalas: Gráfico histórico ajustado a **15 días** para mayor detalle.
    -   Ajuste de densidad de etiquetas (6-7 items) para evitar saturación visual.
    -   Mejorado el espaciado (padding) en los ejes X.
-   **📅 Formato de Fechas**: Estandarización a 2 dígitos (`DD/MM`) en tooltips y modales para una apariencia más profesional.
-   **🖼️ Ajustes UI**:
    -   Centrado vertical perfecto en listas de estadísticas mensuales.
    -   Refinamiento de colores en el tema oscuro.

### v3.0.0 (2026-01-25)
-   **Refactor Completo**: Reescritura del backend a una estructura modular de FastAPI (`app/api`, `app/services`, etc).
-   **Configuración Centralizada**: Implementación de `pydantic-settings` para gestión robusta de configuración y rutas.
-   **Docker**: Optimización de `Dockerfile` y `docker-compose.yml` para despliegues seguros en Portainer.
-   **Limpieza**: Eliminación de scripts legacy y archivos redundantes en la raíz.
-   **UI**: Corrección de unidades de temperatura (ºC) y mejoras visuales.

### v2.1.0
-   Mejoras en gráficas históricas.
-   Soporte para visualización mensual.

### v1.0.0
-   Versión inicial con Flask/FastAPI básico.
