# Usar una imagen ligera de Python (compatible con ARM/RPi)
FROM python:3.10-slim

# Evitar que Python genere archivos pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Evitar buffer en logs
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias (opcional)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar caché de capas (se encuentra en backend/)
COPY backend/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ /app/backend/

# Copiar el frontend (para servir estáticos)
COPY frontend/ /app/frontend/

# Establecer el directorio de trabajo donde está el código a ejecutar
WORKDIR /app/backend

# Comando por defecto (se sobrescribe en docker-compose)
CMD ["python", "-m", "app.services.monitor"]
