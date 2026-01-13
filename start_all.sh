#!/bin/bash

# Script para iniciar Frontend y Backend simultáneamente
# Uso: ./start_all.sh

echo "🚀 Iniciando Sistema Completo - Agente Autónomo"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Deteniendo servicios...${NC}"
    
    # Matar procesos hijos
    pkill -P $$
    
    # Matar procesos en puertos específicos
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    
    echo "${GREEN}✅ Servicios detenidos${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Verificar que estamos en el directorio correcto
if [ ! -f "start_server.sh" ] || [ ! -f "start_frontend.sh" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Limpiar puertos si están ocupados
echo "${BLUE}🔍 Verificando puertos...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "${YELLOW}⚠️  Puerto 8000 ocupado, liberando...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "${YELLOW}⚠️  Puerto 3000 ocupado, liberando...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "${GREEN}✅ Puertos libres${NC}"
echo ""

# Crear directorio de logs si no existe
mkdir -p logs

# Iniciar Backend
echo "${BLUE}🔧 Iniciando Backend API...${NC}"
./start_server.sh > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"

# Esperar a que el backend esté listo
echo "   Esperando a que el backend inicie..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "${GREEN}   ✅ Backend listo en http://localhost:8000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "${YELLOW}   ⚠️  Backend tardó más de lo esperado${NC}"
    fi
done

echo ""

# Iniciar Frontend
echo "${BLUE}🌐 Iniciando Frontend Web Server...${NC}"
./start_frontend.sh > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"

# Esperar a que el frontend esté listo
sleep 2
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "${GREEN}   ✅ Frontend listo en http://localhost:3000${NC}"
else
    echo "${YELLOW}   ⚠️  Frontend puede tardar unos segundos más${NC}"
fi

echo ""
echo "================================================"
echo "${GREEN}✅ Sistema iniciado correctamente${NC}"
echo ""
echo "📍 URLs:"
echo "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo "   Backend:  ${BLUE}http://localhost:8000${NC}"
echo "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "📋 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "💡 Presiona ${YELLOW}Ctrl+C${NC} para detener todos los servicios"
echo "================================================"
echo ""

# Mostrar logs en tiempo real (opcional)
echo "${BLUE}📊 Logs en tiempo real (Backend):${NC}"
tail -f logs/backend.log &
TAIL_PID=$!

# Esperar indefinidamente
wait
