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

1.  **Copiar archivos**:
    Copia toda la carpeta del proyecto a tu RPi (por ejemplo, a `/home/dev/proyectos/monitor_temp_v2`).
    Asegúrate de incluir:
    - `backend/`
    - `frontend/`
    - `Dockerfile`
    - `docker-compose.yml`
    - `requirements.txt`
    - `deploy.sh`

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
