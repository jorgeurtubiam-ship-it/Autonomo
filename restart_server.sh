#!/bin/bash
# Script para reiniciar el backend

echo "🔄 Reiniciando Backend..."

# Detener
./stop_server.sh

# Esperar
sleep 2

# Iniciar
./start_server.sh

echo "✅ Backend reiniciado"
