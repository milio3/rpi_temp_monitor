# Guía de Despliegue en Raspberry Pi (DietPi ARM64 / DOCKHAND)

Esta guía detalla cómo desplegar la versión **v4.0.0** de RPi Temp Monitor en el servidor de producción gestionado con **DOCKHAND**.

---

## 1. Parámetros Operativos Canónicos

- **Host / IP de Producción**: `192.168.1.33`
- **Puerto Host Reservado**: `5300`
- **URL de Acceso Web**: `http://192.168.1.33:5300`
- **Nombre del Contenedor**: `rpi_temp_webapp` (1 único contenedor unificado)
- **Fichero de Orquestación**: `compose.yml`
- **Ruta Canónica de Datos Persistentes en Host**: `/mnt/dietpi_userdata/apps/rpi_temp_monitor/data`
- **Ruta Destino en Contenedor**: `/app/data`

---

## 2. Migración de la Base de Datos Previa (de Dockhand/Portainer a la Ruta Canónica)

Si en el contenedor anterior de Dockhand el origen era una ruta interna de stacks (ej. `/data/compose/9/data`):

1. **Copiar la base de datos previa a la ruta canónica en la RPi:**
   ```bash
   sudo mkdir -p /mnt/dietpi_userdata/apps/rpi_temp_monitor/data
   
   # Si la base de datos previa estaba en /data/compose/9/data:
   sudo cp -v /data/compose/9/data/database.db /mnt/dietpi_userdata/apps/rpi_temp_monitor/data/database.db 2>/dev/null || true

   # Ajustar permisos para el usuario appuser (UID 1000)
   sudo chown -R 1000:1000 /mnt/dietpi_userdata/apps/rpi_temp_monitor/data
   sudo chmod -R 775 /mnt/dietpi_userdata/apps/rpi_temp_monitor/data
   ```

---

## 3. Despliegue con DOCKHAND

1. Abre la interfaz web de **DOCKHAND**.
2. Ve a tus **Stacks / Proyectos** y localiza o crea el stack `rpi_temp_monitor`.
3. Si utilizas Git en Dockhand:
   * **URL del Repositorio**: `https://github.com/milio3/rpi_temp_monitor.git`
   * **Rama / Referencia**: `main` o tag `v4.0.1`
   * **Fichero Compose**: `compose.yml`
4. Comprueba los volúmenes configurados:
   * **Persistencia:** `/mnt/dietpi_userdata/apps/rpi_temp_monitor/data` -> `/app/data`
   * **Sensor Térmico (Solo lectura):** `/sys` -> `/sys:ro`
5. Ejecuta **Deploy / Actualizar Stack** con reconstrucción de imagen (`--build`).

---

## 4. Despliegue Manual por SSH (Alternativa)

```bash
# 1. Conectar por SSH
ssh dev@192.168.1.33

# 2. Situarse en el directorio
cd /opt/apps/rpi_temp_monitor

# 3. Traer últimos cambios y limpiar contenedores legacy
git pull origin main
docker compose down 2>/dev/null || true

# 4. Levantar la nueva versión
docker compose up -d --build

# 5. Comprobar salud y logs
curl -s http://localhost:5300/health
docker compose logs -f webapp
```
