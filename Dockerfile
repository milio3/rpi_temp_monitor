# Usar una imagen ligera de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar caché de capas
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ /app/backend/

# Copiar el frontend (para servir estáticos)
COPY frontend/ /app/frontend/

# Establecer variable de entorno para que Python no buferize logs (útil para ver logs en Docker)
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo en backend para que las importaciones relativas funcionen
WORKDIR /app/backend

# Comando por defecto (se sobrescribe en docker-compose para cada servicio)
CMD ["python", "monitor_service.py"]
