FROM python:3.12-slim

# Gestor ultrarrápido y seguro de dependencias uv oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_NO_CACHE=1

WORKDIR /app

# Crear usuario sin privilegios para mitigar riesgos de seguridad
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Instalar dependencias mínimas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python mediante uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copiar el código fuente modular
COPY app/ ./app/

# Crear directorio de datos persistentes y asignar propiedad al usuario no privilegiado
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
