#!/bin/bash

# Script de Restauración del Agente Autónomo
# Uso: ./restore.sh <archivo_backup.tar.gz>

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debes especificar el archivo de backup${NC}"
    echo ""
    echo "Uso: ./restore.sh <archivo_backup.tar.gz>"
    echo ""
    echo "Backups disponibles:"
    ls -lh ~/backups/agente_autonomo/*.tar.gz 2>/dev/null | awk '{print "  " $9}' || echo "  (ninguno)"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: Archivo no encontrado: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto sobrescribirá el código actual${NC}"
echo -e "${YELLOW}¿Estás seguro? (y/n)${NC}"
read -r response

if [ "$response" != "y" ]; then
    echo "Restauración cancelada"
    exit 0
fi

echo -e "${GREEN}🔄 Iniciando Restauración${NC}"
echo "================================================"

# Detener servicios
echo "🛑 Deteniendo servicios..."
./stop_all.sh 2>/dev/null || true

# Crear backup del estado actual
echo "💾 Creando backup del estado actual..."
SAFETY_BACKUP=~/backups/agente_autonomo/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz
tar -czf "$SAFETY_BACKUP" \
  --exclude='venv' \
  --exclude='__pycache__' \
  -C /Users/lordzero1/IA_LoRdZeRo \
  auto 2>/dev/null || true
echo -e "${GREEN}✅ Backup de seguridad creado${NC}"

# Extraer backup
echo "📦 Extrayendo backup..."
TEMP_DIR=$(mktemp -d)
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Restaurar código
echo "📁 Restaurando código..."
rsync -av --delete \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  "${TEMP_DIR}/auto/" \
  /Users/lordzero1/IA_LoRdZeRo/auto/

# Limpiar
rm -rf "$TEMP_DIR"

echo ""
echo "================================================"
echo -e "${GREEN}✅ Restauración completada${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Verificar dependencias: pip install -r requirements.txt"
echo "2. Restaurar base de datos si es necesario"
echo "3. Iniciar servicios: ./start_all.sh"
echo ""
echo "Backup de seguridad guardado en:"
echo "  $SAFETY_BACKUP"
echo "================================================"
