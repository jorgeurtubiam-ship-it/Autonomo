#!/bin/bash

# Script para detener todos los servicios
# Uso: ./stop_all.sh

echo "🛑 Deteniendo Sistema Completo - Agente Autónomo"
echo "================================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detener procesos en puertos
echo "${YELLOW}Deteniendo Backend (puerto 8000)...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Backend detenido${NC}"
else
    echo "   (No había proceso en puerto 8000)"
fi

echo ""
echo "${YELLOW}Deteniendo Frontend (puerto 3000)...${NC}"
lsof -ti:3000 | xargs kill -9 2>/dev/null
if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Frontend detenido${NC}"
else
    echo "   (No había proceso en puerto 3000)"
fi

# Limpiar procesos de uvicorn y http.server
echo ""
echo "${YELLOW}Limpiando procesos residuales...${NC}"
pkill -f "uvicorn backend.api.main:app" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
echo "${GREEN}✅ Limpieza completada${NC}"

echo ""
echo "================================================"
echo "${GREEN}✅ Todos los servicios detenidos${NC}"
echo "================================================"
