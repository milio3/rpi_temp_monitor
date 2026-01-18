# Monitor de Temperatura - Raspberry Pi

Sistema de monitoreo de temperatura de CPU para Raspberry Pi con visualización web en tiempo real.

## Características

- Lectura automática de temperatura de CPU cada 10 minutos
- Dashboard web con gráficos interactivos (últimas 24 horas y histórico)
- Sistema de alertas por umbrales configurables
- Consolidación automática de datos diarios
- Actualización automática de la interfaz sin recargar página
- Indicadores visuales de estado (normal/warning/critical)
- Tema oscuro/claro con selector

## Estructura del Proyecto

```
monitor_temp/
├── log_temp.py          # Script principal de monitoreo
├── config.py            # Configuración centralizada
├── template.html        # Plantilla HTML para el dashboard
├── index.html          # Dashboard generado (actualizado automáticamente)
├── temp.log            # Registro de temperaturas
├── alerts.log          # Registro de alertas
├── monitor.log         # Log del sistema
└── requirements.txt    # Dependencias (vacío, solo stdlib)
```

## Instalación

1. Clonar o copiar los archivos al directorio del proyecto:
   ```bash
   cd /home/dev/proyectos/monitor_temp
   ```

2. Asegurar permisos de ejecución:
   ```bash
   chmod +x log_temp.py
   ```

3. Probar manualmente:
   ```bash
   python3 log_temp.py
   ```

4. Configurar crontab para ejecución automática:
   ```bash
   crontab -e
   ```
   
   Añadir la siguiente línea para ejecutar cada 10 minutos:
   ```
   */10 * * * * /usr/bin/python3 /home/dev/proyectos/monitor_temp/log_temp.py
   ```

   Para consolidar datos diarios al inicio del día, añadir también:
   ```
   1 0 * * * /usr/bin/python3 /home/dev/proyectos/monitor_temp/log_temp.py
   ```

## Servidor Web

Para servir el dashboard, usar el servidor HTTP de Python:

```bash
cd /home/dev/proyectos/monitor_temp
python3 -m http.server 8080
```

**Nota**: El puerto 8080 evita la necesidad de permisos root. Para usar puerto 80, ejecutar con `sudo`.

Para ejecutar en segundo plano:

```bash
nohup python3 -m http.server 8080 > /dev/null 2>&1 &
```

El dashboard estará disponible en: `http://localhost:8080`

## Formato de Log

### temp.log

Formato de líneas DATA:
```
YYYY-MM-DD HH:MM:SS | temperatura | DATA
```

Formato de líneas SUMMARY (consolidación diaria):
```
YYYY-MM-DD 00:00:00 | min_temp (HH:MM)/max_temp (HH:MM) | SUMMARY
```

Ejemplo:
```
2026-01-18 01:50:01 | 39.92 | DATA
2026-01-17 00:00:00 | 36.51 (00:00)/42.84 (23:50) | SUMMARY
```

### alerts.log

Registra alertas cuando la temperatura supera los umbrales:
```
YYYY-MM-DD HH:MM:SS | temperatura | WARNING/CRITICAL
```

## Configuración

Editar `config.py` para personalizar los parámetros:

- `TEMP_WARNING_THRESHOLD`: 70.0°C - Umbral de advertencia
- `TEMP_CRITICAL_THRESHOLD`: 80.0°C - Umbral crítico
- `DAILY_HOURS`: 24 - Horas de datos diarios a mostrar
- `HISTORY_DAYS`: 10 - Días de historial a mostrar
- `TEMP_MIN_VALID`: 0.0°C - Temperatura mínima válida
- `TEMP_MAX_VALID`: 100.0°C - Temperatura máxima válida

## Funcionamiento

1. **Lectura de temperatura**: El script lee `/sys/class/thermal/thermal_zone0/temp` (en milidegrees)
2. **Validación**: Verifica que la temperatura esté en rango válido (0-100°C)
3. **Logging**: Escribe la temperatura en `temp.log`
4. **Alertas**: Si supera umbrales, registra en `alerts.log`
5. **Consolidación**: Al inicio del día, consolida datos del día anterior
6. **Generación HTML**: Actualiza `index.html` con datos actualizados y gráficos

## Características del Dashboard

- **Actualización automática**: La página se actualiza cada 60 segundos sin recargar
- **Indicadores de estado**:
  - Verde: < 70°C (normal)
  - Naranja: 70-80°C (advertencia)
  - Rojo: > 80°C (crítico)
- **Tema oscuro/claro**: Selector de tema en la interfaz
- **Botón de refresh**: Actualización manual de datos
- **Gráficos interactivos**: Chart.js para visualización de datos

## Mantenimiento

- Los logs pueden crecer con el tiempo. Considerar rotación periódica
- El `index.html` se regenera en cada ejecución
- Las alertas se acumulan en `alerts.log` - revisar periódicamente
- Revisar `monitor.log` para logs del sistema y errores

## Solución de Problemas

**Temperatura siempre 0.0°C o None**:
- Verificar que el sensor existe: `cat /sys/class/thermal/thermal_zone0/temp`
- Verificar permisos de lectura

**No se genera index.html**:
- Verificar que `template.html` existe y tiene permisos de lectura
- Revisar `monitor.log` para errores

**Gráficos vacíos**:
- Verificar que `temp.log` contiene datos
- Verificar formato de líneas en el log

**ImportError al ejecutar**:
- El script funciona sin `config.py` usando valores por defecto
- Si creas `config.py`, asegúrate de que tenga la sintaxis correcta

## Licencia

Este proyecto es de uso libre para monitoreo personal.
