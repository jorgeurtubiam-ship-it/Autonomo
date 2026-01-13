# Backend Dockerfile
FROM python:3.10-slim

# Instalar dependencias del sistema para OpenCV y WebRTC
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ ./backend/

# Variables de entorno
ENV PYTHONPATH=/app/backend

# Exponer el puerto de la API
EXPOSE 8000

# Comando para iniciar la API
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
