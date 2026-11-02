# Guía de Despliegue en Raspberry Pi (DietPi ARM64 / Portainer)

Esta guía detalla cómo desplegar la versión **v4.0.0** de RPi Temp Monitor en el servidor de producción.

---

## 1. Parámetros de Operación

- **Host / IP de Producción**: `192.168.1.33`
- **Puerto Host Reservado**: `8085`
- **URL de Acceso Web**: `http://192.168.1.33:8085`
- **Nombre del Contenedor**: `rpi_temp_webapp`
- **Fichero de Orquestación**: `compose.yml`
- **Directorio de Datos Persistentes en Host**: `/mnt/dietpi_userdata/apps/rpi_temp_monitor/data`

---

## 2. Despliegue mediante Portainer

1. Accede a tu consola de Portainer en la Raspberry Pi.
2. Ve a la sección **Stacks** y pulsa **Add stack**.
3. Selecciona el método **Repository**:
   - **Name**: `rpi_temp_monitor`
   - **Repository URL**: *(URL del repositorio en GitHub)*
   - **Repository reference**: `refs/tags/v4.0.0` (o rama `main`)
   - **Compose path**: `compose.yml`
4. Pulsa **Deploy the stack**.

---

## 3. Despliegue mediante CLI en Raspberry Pi

```bash
# 1. Conectar por SSH
ssh dev@192.168.1.33

# 2. Situarse en el directorio de la aplicación
cd /opt/apps/rpi_temp_monitor

# 3. Descargar la versión deseada
git fetch --tags
git checkout v4.0.0

# 4. Asegurar permisos en el directorio de persistencia
sudo mkdir -p /mnt/dietpi_userdata/apps/rpi_temp_monitor/data
sudo chown -R 1000:1000 /mnt/dietpi_userdata/apps/rpi_temp_monitor/data

# 5. Levantar el servicio
docker compose up -d --build

# 6. Comprobar salud y logs
curl -f http://localhost:8085/health
docker compose logs -f webapp
```

---

## 4. Notas Técnicas de la Versión 4.0.0

- **1 Único Contenedor**: Se ha unificado el servicio web y la captura de datos térmica en un solo proceso con el ciclo de vida `lifespan` de FastAPI, reduciendo el consumo de RAM a menos de 512 MB.
- **Acceso a Hardware Térmico**: El contenedor mapea `/sys:/sys:ro` para leer directamente la temperatura de la CPU desde `/sys/class/thermal/thermal_zone0/temp` en la Raspberry Pi.
- **Persistencia Segura**: La base de datos SQLite se ejecuta con `journal_mode=WAL` y `synchronous=NORMAL` para máxima integridad estructural.
