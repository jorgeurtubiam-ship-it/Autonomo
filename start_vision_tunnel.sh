#!/bin/bash

# Script para iniciar el túnel de visión (HTTPS)
# Esto es necesario porque los móviles bloquean el acceso a la cámara en HTTP
# Uso: ./start_vision_tunnel.sh

echo "🌐 Iniciando Túnel de Visión - Agente Autónomo"
echo "================================================"

# Verificar si npx está instalado
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx no está instalado. Instala Node.js para continuar."
    exit 1
fi

echo "🚀 Exponiendo el sistema (puerto 8000) a internet vía HTTPS..."
echo "💡 Nota: Usa la URL que termine en '.loca.lt'"
echo ""

# Iniciar localtunnel en el puerto 8000 con el subdominio deseado
npx localtunnel --port 8000 --subdomain vision-agente-zero
