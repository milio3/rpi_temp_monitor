# Guía de Despliegue en Raspberry Pi (Portainer)

Esta guía detalla cómo desplegar el Monitor de Temperatura utilizando **Portainer**.

## Datos de Despliegue

-   **IP Raspberry Pi**: `192.168.1.33`
-   **Puerto Web**: `8085`
-   **URL de Acceso**: `http://192.168.1.33:8085`

## 1. Configuración en Portainer

1.  Accede a tu instancia de Portainer.
2.  Ve al apartado **Stacks** y pulsa en **Add stack**.
3.  Selecciona la opción **Repository** (para que se actualice desde GitHub/Git).
4.  Rellena los campos:
    -   **Name**: `rpi_temp_monitor`
    -   **Repository URL**: *(La URL de tu repositorio GitHub)*
    -   **Repository reference**: `refs/heads/main` (o la rama donde tengas este código, ej: `feature/backend-refactor`)
    -   **Compose path**: `docker-compose.yml`
5.  Variables de entorno (Opcional, ya definidas en el fichero, pero puedes sobrescribirlas):
    -   `TZ`: `Europe/Madrid`
6.  Pulsa **Deploy the stack**.

## 2. Verificación

Una vez el stack esté en estado "Running":

1.  Abre un navegador web.
2.  Navega a: `http://192.168.1.33:8085`
3.  Deberías ver la interfaz del monitor.

## 3. Migración de Datos (Log antiguo)

Si tienes un fichero `temp.log` antiguo y quieres importar sus datos:

1.  Localiza dónde tienes el fichero `temp.log` en tu Raspberry Pi (por ejemplo `/home/pi/temp.log`).
2.  Conéctate por SSH a la RPi.
3.  Copia el fichero dentro del contenedor del monitor:
    ```bash
    # Identifica el ID del contenedor
    docker ps | grep monitor
    
    # Copia el fichero (sustituye <CONTAINER_ID>)
    docker cp /home/pi/temp.log <CONTAINER_ID>:/app/backend/temp_legacy.log
    ```
4.  Ejecuta el script de migración incluído:
    ```bash
    docker exec -it <CONTAINER_ID> python scripts/migrate_legacy.py --log-file temp_legacy.log
    ```

## Notas Técnicas

-   **Sin deploy.sh**: El script `deploy.sh` antiguo se ha movido a `scripts/deploy.sh` pero **no es necesario** si usas Portainer.

## 4. Solución de Errores Comunes

### Error: "attempt to write a readonly database"

Si ves este error en los logs, es porque el contenedor ahora corre como usuario no privilegiado (`1000:1000`) por seguridad, pero la carpeta de datos pertenece a `root`.

**Solución**:
Ejecuta este comando en la terminal de tu Raspberry Pi para dar permisos al usuario por defecto:

```bash
# Si usas una ruta volumen personalizada (ej: /home/pi/rpi_data)
sudo chown -R 1000:1000 /home/pi/rpi_data

# Si usas la ruta por defecto de Portainer/Docker (busca tu volumen)
# Opción rápida: dar permisos a 'otros' (menos seguro pero funcional en entornos aislados)
sudo chmod 777 -R path/to/your/volume
```
