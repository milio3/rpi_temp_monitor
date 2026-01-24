# Guía de Instalación en Raspberry Pi

Esta guía te ayudará a instalar el Monitor de Temperatura en tu Raspberry Pi utilizando Docker.

## Prerrequisitos

1.  **Docker y Docker Compose**: Asegúrate de tenerlos instalados en tu RPi.
    ```bash
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    sudo apt-get install -y docker-compose
    # Cerrar sesión y volver a entrar para aplicar cambios de grupo
    ```

## Instalación

1.  **Clonar y preparar repositorio**:
    En tu Raspberry Pi, clona el repositorio y cambia a la rama de migración:
    ```bash
    cd /home/dev/proyectos/
    git clone <URL_TU_REPOSITORIO> monitor_temp_v2
    cd monitor_temp_v2
    git fetch origin
    git checkout feature/docker-migration
    ```

2.  **Preparar script de despliegue**:
    Da permisos de ejecución al script:
    ```bash
    chmod +x deploy.sh
    ```

3.  **Ejecutar despliegue**:
    Ejecuta el script. Este se encargará de crear las carpetas necesarias, construir los contenedores y lanzarlos.
    ```bash
    ./deploy.sh
    ```
    
    Durante la ejecución, te preguntará si quieres importar datos antiguos. Dile que sí ("s") si tienes tu fichero `temp.log` en la ruta `/home/dev/proyectos/monitor_temp/temp.log`.

## Opción B: Despliegue con Portainer

Si prefieres usar **Portainer** para gestionar tus contenedores:

1.  Accede a tu Portainer.
2.  Ve a **Stacks** > **Add stack**.
3.  Selecciona **Repository**.
4.  Rellena los datos:
    - **Name**: `rpi_temp_monitor`
    - **Repository URL**: La URL de tu repositorio Github.
    - **Repository reference**: `refs/heads/feature/docker-migration` (¡Importante! Estamos en una rama).
    - **Compose path**: `docker-compose.yml`
5.  Haz clic en **Deploy the stack**.

**Nota sobre la migración de datos con Portainer**:
El script automático `deploy.sh` no se ejecuta en Portainer. Para migrar los datos:
1. Una vez el stack esté corriendo ("Deployed"), conéctate por SSH a tu Raspberry Pi.
2. Ejecuta los siguientes comandos para copiar tu log dentro del contenedor y lanzar la migración:
   ```bash
   # Copiar fichero al contenedor
   sudo docker cp /home/dev/proyectos/monitor_temp/temp.log rpi_temp_monitor:/app/temp_legacy.log
   
   # Ejecutar script de migración dentro del contenedor
   sudo docker exec rpi_temp_monitor python migrate_legacy.py --log-file /app/temp_legacy.log
   ```

## Funcionamiento Automático

- La aplicación está configurada con `restart: always`. Esto significa que **arrancará automáticamente** cada vez que enciendas la Raspberry Pi o si se recupera de un fallo de luz/internet. No necesitas configurar systemd manualmente.

## Verificación

- Accede a `http://<IP-DE-TU-RPI>:8085` desde tu navegador.
- Deberías ver la gráfica de temperatura actual e histórica.

## Solución de Problemas

- **Ver logs**:
  ```bash
  docker-compose logs -f
  ```
- **Reiniciar servicios manualmente**:
  ```bash
  docker-compose restart
  ```
