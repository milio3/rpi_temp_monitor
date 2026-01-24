#!/bin/bash

# Script de Despliegue para RPi Temp Monitor

# Colores para output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Iniciando despliegue de RPi Temp Monitor...${NC}"

# Detector comando docker compose (V1 vs V2)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo -e "\033[0;31mError: No se encontró 'docker-compose' ni 'docker compose'. Por favor instala Docker Compose.\033[0m"
    exit 1
fi

# 1. Crear directorios necesarios
echo "Creando directorios locales..."
mkdir -p data

# 2. Construir e Iniciar Contenedores
echo -e "${GREEN}Construyendo y levantando contenedores Docker...${NC}"
$DOCKER_COMPOSE_CMD up -d --build

# 3. Esperar un momento a que los servicios arranquen (opcional, pero buena práctica si fueramos a atacar la API)
sleep 5

# 4. Migración de Datos (opcional)
# Preguntar al usuario si quiere migrar
read -p "¿Deseas importar datos antiguos desde el log? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    LOG_PATH="/home/dev/proyectos/monitor_temp/temp.log"
    echo -e "${GREEN}Ejecutando script de migración buscando en $LOG_PATH...${NC}"
    
    # Ejecutamos el script DENTRO del contenedor monitor para tener acceso al entorno python y DB
    # Asumimos que el log está en el host en la ruta indicada. 
    # Para que el contenedor lo vea, necesitaríamos montarlo. 
    # Como no lo hemos montado en docker-compose por defecto, lo haremos con un 'docker run' efímero o añadimos volumen temporal.
    # O más fácil: pedir al usuario que ponga el log en ./legacy/temp.log y lo montamos?
    # El usuario dijo que el fichero está en "/home/dev/proyectos/monitor_temp/temp.log".
    # Vamos a usar 'docker cp' para meterlo temporalmente o montarlo.
    
    if [ -f "$LOG_PATH" ]; then
        # Copiar log al contenedor
        docker cp "$LOG_PATH" rpi_temp_monitor:/app/temp_legacy.log
        
        # Ejecutar script
        docker exec rpi_temp_monitor python migrate_legacy.py --log-file /app/temp_legacy.log
        
        echo -e "${GREEN}Migración finalizada.${NC}"
    else
        echo "No se encontró el fichero en $LOG_PATH. Saltando migración."
        echo "Si deseas migrar manualmente, copia el fichero y ejecuta:"
        echo "docker cp /ruta/al/log rpi_temp_monitor:/app/temp.log"
        echo "docker exec rpi_temp_monitor python migrate_legacy.py --log-file /app/temp.log"
    fi
fi

echo -e "${GREEN}Despliegue completado!${NC}"
echo "Accede a la web en: http://localhost:8085"
