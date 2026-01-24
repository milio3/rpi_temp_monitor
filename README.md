# Monitor de Temperatura - Raspberry Pi (v2.1)

Sistema de monitoreo profesional de temperatura para Raspberry Pi utilizando **FastAPI**, **SQLite** y una **SPA** moderna.

## Características

- **Arquitectura Cliente-Servidor**: Backend FastAPI + Frontend HTML/JS desacoplado.
- **Base de Datos SQLite**: Almacenamiento eficiente de lecturas históricas.
- **Visualización Avanzada**:
  - Gráfico de actividad 24h (intervalos de 1 hora, interpolados).
  - Histórico de 30 días (Mínimas y Máximas diarias).
  - **Modal de Estadísticas**: Histórico completo mensual organizado por años.
- **Resilient**: Servicio de monitoreo independiente que persiste datos ante caídas del servidor web.
- **Interfaz Reactiva**: Actualización en tiempo real sin recargas de página.

## Estructura del Proyecto

```
rpi_temp_monitor/
├── backend/
│   ├── app/
│   │   ├── main.py          # API Web Server (FastAPI)
│   │   ├── models.py        # Modelos de Datos (SQLModel)
│   │   └── database.py      # Conexión DB
│   ├── monitor_service.py   # Servicio de lectura de sensores (Background)
│   ├── seed_full_reboot.py  # Script de utilidad (Reset DB)
│   └── database.db          # Base de datos SQLite
├── frontend/
│   ├── index.html           # Single Page Application
│   └── js/
│       └── app.js           # Lógica Frontend
└── requirements.txt
```

## Instalación y Ejecución

### 1. Prerrequisitos
- Python 3.9+
- Entorno virtual (recomendado)

### 2. Configuración Inicial
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 3. Ejecutar Servicios
Se necesitan dos terminales (o configurar como servicios systemd):

**Terminal 1: Servidor Web (Backend + Frontend)**
```bash
# Desde la carpeta raíz del proyecto
cd backend
../venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Acceder a: `http://localhost:8000`

**Terminal 2: Servicio de Monitoreo**
Este script lee la temperatura cada 10 minutos y la guarda en SQLite.
```bash
# Desde la carpeta raíz del proyecto
cd backend
../venv/Scripts/python monitor_service.py
```

## Migración de Datos (Opcional)
Si necesitas reiniciar la base de datos e importar datos antiguos (`legacy/temp.log`):
```bash
cd backend
../venv/Scripts/python seed_full_reboot.py
```

## Configuración en Raspberry Pi (Systemd)
Para que arranque automáticamente, crea dos servicios en `/etc/systemd/system/`:

1. `rpi-monitor-web.service` (para uvicorn)
2. `rpi-monitor-logger.service` (para monitor_service.py)
