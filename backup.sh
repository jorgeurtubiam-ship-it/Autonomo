#!/bin/bash

# Script de Backup Automático del Agente Autónomo
# Uso: ./backup.sh

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Iniciando Backup del Agente Autónomo${NC}"
echo "================================================"

# Crear directorio de backups
BACKUP_DIR=~/backups/agente_autonomo
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_${TIMESTAMP}"

echo -e "${YELLOW}📦 Creando backup: ${BACKUP_NAME}${NC}"

# Backup del código
echo "📁 Respaldando código fuente..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='logs/*.log' \
  -C /Users/lordzero1/IA_LoRdZeRo \
  auto

BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
echo -e "${GREEN}✅ Código respaldado (${BACKUP_SIZE})${NC}"

# Backup de la base de datos
if [ -f ~/.agent_data/conversations/agent.db ]; then
    echo "💾 Respaldando base de datos..."
    cp ~/.agent_data/conversations/agent.db \
       "${BACKUP_DIR}/agent_db_${TIMESTAMP}.db"
    DB_SIZE=$(du -h "${BACKUP_DIR}/agent_db_${TIMESTAMP}.db" | cut -f1)
    echo -e "${GREEN}✅ Base de datos respaldada (${DB_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠️  No se encontró base de datos${NC}"
fi

# Backup de screenshots (si existen)
if [ -d ~/.agent_data/screenshots ]; then
    echo "📸 Respaldando screenshots..."
    tar -czf "${BACKUP_DIR}/screenshots_${TIMESTAMP}.tar.gz" \
      -C ~/.agent_data \
      screenshots
    SCREENSHOTS_SIZE=$(du -h "${BACKUP_DIR}/screenshots_${TIMESTAMP}.tar.gz" | cut -f1)
    echo -e "${GREEN}✅ Screenshots respaldados (${SCREENSHOTS_SIZE})${NC}"
fi

# Crear archivo de información
cat > "${BACKUP_DIR}/${BACKUP_NAME}_info.txt" << EOF
Backup del Agente Autónomo
==========================

Fecha: $(date)
Timestamp: ${TIMESTAMP}

Archivos incluidos:
- Código fuente completo
- Base de datos SQLite
- Screenshots
- Documentación
- Configuración

Excluidos:
- venv (entorno virtual)
- __pycache__
- .git
- logs

Para restaurar:
1. Extraer: tar -xzf ${BACKUP_NAME}.tar.gz
2. Restaurar DB: cp agent_db_${TIMESTAMP}.db ~/.agent_data/conversations/agent.db
3. Instalar dependencias: pip install -r requirements.txt
4. Iniciar: ./start_all.sh
EOF

echo ""
echo "================================================"
echo -e "${GREEN}✅ Backup completado exitosamente${NC}"
echo ""
echo "📍 Ubicación: ${BACKUP_DIR}"
echo "📦 Archivos:"
ls -lh "${BACKUP_DIR}" | grep "${TIMESTAMP}" | awk '{print "   - " $9 " (" $5 ")"}'
echo ""
echo "================================================"

# Limpiar backups antiguos (mantener últimos 10)
echo -e "${YELLOW}🧹 Limpiando backups antiguos...${NC}"
cd "${BACKUP_DIR}"
ls -t backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
ls -t agent_db_*.db 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
echo -e "${GREEN}✅ Limpieza completada (manteniendo últimos 10)${NC}"

echo ""
echo -e "${GREEN}🎉 ¡Backup finalizado!${NC}"
