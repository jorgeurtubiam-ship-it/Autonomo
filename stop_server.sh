#!/bin/bash
# Script para detener el backend

echo "🛑 Deteniendo Backend..."

# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Backend detenido"
else
    echo "⚠️  No había backend corriendo"
fi
