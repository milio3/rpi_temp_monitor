# Especificación Funcional: Renovación de Arquitectura e Interfaz de RPi Temp Monitor (v4.0.0)

## 1. Contexto y Objetivos

El proyecto **RPi Temp Monitor** se diseñó originalmente para monitorizar la temperatura de la CPU en una Raspberry Pi (DietPi ARM64) y presentar un historial visual. En su versión 3.1, la infraestructura utilizaba dos contenedores independientes (`webapp` y `monitor`) que compartían el archivo de base de datos SQLite y mantenían el frontend y backend desacoplados como archivos estáticos independientes.

### Metas de la Versión 4.0.0:
1. **Unificación de Infraestructura:** Consolidar el servicio en un único contenedor Docker (`rpi_temp_webapp`) ejecutando FastAPI en el puerto host 8085. La captura periódica de temperatura se ejecutará como una tarea asíncrona nativa en el ciclo de vida (*lifespan*) de FastAPI, eliminando contención en SQLite, redundancia de contenedores y simplificando el despliegue.
2. **Interfaz Web Canónica y Ergonómica (WCAG 2.2 AA):** Reemplazar el frontend estático por una arquitectura fullstack integrada en FastAPI (Jinja2 + HTMX + Alpine.js + Tailwind CSS) siguiendo la directiva `ui-dark-dashboard`. Adaptado a monitor QHD 32", con paleta grafito/carbón, tipografía funcional mínima de 15-18px y cero parpadeos.
3. **Mayor Riqueza de Información:**
   - Visualización de temperatura en tiempo real con indicador semántico de estado térmico.
   - Métricas agregadas de 24 horas: Temperatura mínima, máxima y promedio del día.
   - Margen térmico (*Thermal Headroom*) respecto al límite de estrangulamiento térmico de la Raspberry Pi (80 °C).
   - Historial mensual estructurado con mínimos y máximos temporizados.
   - Gráficas interactivas optimizadas para tema oscuro: actividad de 24 horas y tendencia histórica de 30 días.
   - Indicador de estado del sensor (físico `/sys/...` vs simulador en desarrollo), total de lecturas en base de datos y marca temporal de la última captura.
   - Exportación de lecturas completas a CSV.
4. **Cumplimiento Estricto de la Constitución (`GEMINI.md`):**
   - Endpoints estándar `GET /health` y `GET /ready`.
   - SQLite en modo WAL con `synchronous=NORMAL`, `foreign_keys=ON` y `busy_timeout=10000`.
   - Gestión con `uv`, construcción hardened en Dockerfile y límites en `compose.yml`.
   - Suite de tests con aislamiento de base de datos en Python 3.15 y Python 3.12.

---

## 2. Criterios de Aceptación (Gherkin)

### Escenario 1: Captura continua en único proceso/contenedor
- **Dado que** el servicio FastAPI arranca mediante su ciclo de vida *lifespan*,
- **Cuando** se inicializa la aplicación,
- **Entonces** debe ejecutar una lectura térmica inmediata e iniciar una tarea en segundo plano que capture la temperatura cada intervalo configurado (por defecto 600 segundos) y la guarde en SQLite sin bloquear peticiones HTTP.

### Escenario 2: Visualización ergonómica en tiempo real (HTMX)
- **Dado que** un usuario accede a la raíz del servicio (`GET /`),
- **Cuando** carga el dashboard,
- **Entonces** debe visualizar la temperatura actual, tarjetas KPI de 24h, margen térmico y gráficas de actividad,
- **Y además** la tarjeta de temperatura actual debe actualizarse dinámicamente mediante HTMX cada 30 segundos sin recargar la página.

### Escenario 3: Endpoints de salud y observabilidad
- **Dado que** un orquestador o usuario consulta `GET /health`,
- **Cuando** la aplicación está activa,
- **Entonces** debe retornar código 200 con JSON `{"status": "ok", "version": "4.0.0", "timestamp": "..."}`,
- **Y cuando** se consulta `GET /ready`, debe verificar la conexión activa a SQLite antes de devolver 200.

### Escenario 4: Auditoría y exportación de datos
- **Dado que** existen más de 50.000 registros históricos en la base de datos,
- **Cuando** el usuario solicita `GET /api/v1/readings/export/csv`,
- **Entonces** debe recibir un archivo CSV descargable con todas las lecturas registradas ordenadas cronológicamente.

### Escenario 5: Entorno de desarrollo multiplataforma
- **Dado que** la aplicación se ejecuta en Windows o en un host sin `/sys/class/thermal/thermal_zone0/temp`,
- **Cuando** se realiza la lectura de temperatura,
- **Entonces** debe detectar la ausencia del sensor físico y generar una simulación controlada sin generar errores fatales.

---

## 3. Límites y Casos Borde

1. **Sensor no disponible o lectura corrupta:** Si la lectura del archivo `/sys/...` produce una excepción o valor no numérico, el servicio registrará un aviso en el log y conservará el estado anterior sin abortar el ciclo de monitorización.
2. **Aislamiento en pruebas:** Los tests automatizados bajo ningún concepto tocarán `data/database.db` ni `backend/database.db`. Se utilizará una base de datos SQLite en memoria o temporal efímera inyectada vía dependencias de FastAPI.
3. **Persistencia y Compatibilidad:** La tabla existente `temperaturereading` debe respetarse exactamente para mantener la compatibilidad con los 53.000+ registros históricos existentes.
