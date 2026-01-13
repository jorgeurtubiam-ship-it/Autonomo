#!/bin/bash

# Script para iniciar el frontend
# Sirve los archivos HTML/CSS/JS en puerto 3000

echo "🌐 Iniciando Frontend Web Server..."
echo "📁 Directorio: frontend/"
echo "🔗 URL: http://localhost:3000"
echo ""
echo "✅ Servidor iniciando..."
echo "💡 Presiona Ctrl+C para detener"
echo ""

cd frontend
python3 -m http.server 3000
