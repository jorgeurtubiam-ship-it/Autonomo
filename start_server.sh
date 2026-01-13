#!/bin/bash

# Script para iniciar el servidor API
# Con entorno virtual y PYTHONPATH configurado

echo "🚀 Iniciando Backend API..."

# Activar entorno virtual
source venv/bin/activate

# Configurar PYTHONPATH
export PYTHONPATH="/Users/lordzero1/IA_LoRdZeRo/auto:/Users/lordzero1/IA_LoRdZeRo/auto/backend:$PYTHONPATH"

# Configuración de Túnel de Visión (HTTPS)
export VISION_TUNNEL_URL="https://vision-agente-zero.loca.lt"

# Iniciar servidor
echo "✅ Servidor iniciando en http://localhost:8000"
echo "📚 Documentación: http://localhost:8000/docs"
echo ""

python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
