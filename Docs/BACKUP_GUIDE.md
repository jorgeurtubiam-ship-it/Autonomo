# 💾 Sistema de Backup y Restauración

## 📋 Resumen

Se ha creado un sistema completo de backup y restauración para el Agente Autónomo.

---

## ✅ Backup Actual

**Fecha:** 2025-12-27 18:15:05

**Archivos respaldados:**
- ✅ Código fuente completo (162 KB)
- ✅ Base de datos SQLite (80 KB)
- ✅ Documentación
- ✅ Configuración
- ✅ Scripts

**Ubicación:**
```
~/backups/agente_autonomo/
├── backup_20251227_181505.tar.gz    (162 KB)
└── agent_db_backup_20251227_181506.db (80 KB)
```

---

## 🛠️ Scripts Creados

### 1. `backup.sh` - Backup Automático

**Uso:**
```bash
./backup.sh
```

**Qué hace:**
- ✅ Crea backup comprimido del código
- ✅ Respalda base de datos SQLite
- ✅ Respalda screenshots (si existen)
- ✅ Genera archivo de información
- ✅ Limpia backups antiguos (mantiene últimos 10)

**Excluye:**
- venv (entorno virtual)
- __pycache__
- .git
- logs
- node_modules

---

### 2. `restore.sh` - Restauración

**Uso:**
```bash
./restore.sh ~/backups/agente_autonomo/backup_20251227_181505.tar.gz
```

**Qué hace:**
- ✅ Detiene servicios
- ✅ Crea backup de seguridad del estado actual
- ✅ Restaura código desde backup
- ✅ Preserva configuración importante

**Seguridad:**
- Pide confirmación antes de restaurar
- Crea backup del estado actual antes de sobrescribir

---

## 📅 Programar Backups Automáticos

### Opción 1: Cron (Diario a las 2 AM)

```bash
# Editar crontab
crontab -e

# Agregar línea:
0 2 * * * cd /Users/lordzero1/IA_LoRdZeRo/auto && ./backup.sh >> ~/backups/backup.log 2>&1
```

### Opción 2: Manual

```bash
# Ejecutar cuando quieras
cd /Users/lordzero1/IA_LoRdZeRo/auto
./backup.sh
```

---

## 🔄 Restaurar desde Backup

### Paso 1: Listar backups disponibles

```bash
ls -lh ~/backups/agente_autonomo/
```

### Paso 2: Restaurar

```bash
cd /Users/lordzero1/IA_LoRdZeRo/auto
./restore.sh ~/backups/agente_autonomo/backup_YYYYMMDD_HHMMSS.tar.gz
```

### Paso 3: Reinstalar dependencias

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Paso 4: Restaurar base de datos (opcional)

```bash
cp ~/backups/agente_autonomo/agent_db_backup_YYYYMMDD_HHMMSS.db \
   ~/.agent_data/conversations/agent.db
```

### Paso 5: Iniciar sistema

```bash
./start_all.sh
```

---

## 📊 Qué se Respalda

### ✅ Incluido en Backup

- **Código fuente:**
  - backend/
  - frontend/
  - tools/
  - scripts/

- **Configuración:**
  - requirements.txt
  - .env (si existe)
  - Scripts de inicio/detención

- **Documentación:**
  - Docs/
  - README.md
  - DOCUMENTATION.md

- **Base de datos:**
  - agent.db (conversaciones, mensajes, API keys)

### ❌ Excluido del Backup

- venv/ (se reinstala con pip)
- __pycache__/ (se regenera)
- .git/ (historial de git)
- logs/*.log (logs temporales)
- node_modules/ (se reinstala con npm)

---

## 🔒 Seguridad

### API Keys

**⚠️ IMPORTANTE:** Las API keys están en la base de datos.

**Recomendaciones:**
1. Encriptar backups si contienen API keys
2. Almacenar backups en ubicación segura
3. No compartir backups públicamente

**Encriptar backup:**
```bash
# Encriptar
gpg -c ~/backups/agente_autonomo/backup_20251227_181505.tar.gz

# Desencriptar
gpg ~/backups/agente_autonomo/backup_20251227_181505.tar.gz.gpg
```

---

## 📍 Ubicaciones Importantes

```
~/backups/agente_autonomo/          # Backups
~/.agent_data/conversations/        # Base de datos
~/.agent_data/screenshots/          # Screenshots
/Users/lordzero1/IA_LoRdZeRo/auto/  # Código fuente
```

---

## 🆘 Recuperación de Desastres

### Escenario 1: Código corrupto

```bash
./restore.sh ~/backups/agente_autonomo/backup_LATEST.tar.gz
pip install -r requirements.txt
./start_all.sh
```

### Escenario 2: Base de datos corrupta

```bash
cp ~/backups/agente_autonomo/agent_db_backup_LATEST.db \
   ~/.agent_data/conversations/agent.db
./restart_server.sh
```

### Escenario 3: Sistema completo perdido

```bash
# 1. Restaurar código
mkdir -p /Users/lordzero1/IA_LoRdZeRo
cd /Users/lordzero1/IA_LoRdZeRo
tar -xzf ~/backups/agente_autonomo/backup_LATEST.tar.gz

# 2. Crear venv
cd auto
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Restaurar DB
mkdir -p ~/.agent_data/conversations
cp ~/backups/agente_autonomo/agent_db_backup_LATEST.db \
   ~/.agent_data/conversations/agent.db

# 5. Iniciar
./start_all.sh
```

---

## 📝 Notas

- Los backups se limpian automáticamente (mantiene últimos 10)
- Cada backup incluye archivo `_info.txt` con detalles
- El script `restore.sh` crea backup de seguridad antes de restaurar
- Tamaño típico de backup: ~200-300 KB (sin venv)

---

## 🔍 Verificar Backup

```bash
# Ver contenido del backup
tar -tzf ~/backups/agente_autonomo/backup_20251227_181505.tar.gz | head -20

# Ver tamaño
du -h ~/backups/agente_autonomo/backup_20251227_181505.tar.gz

# Verificar integridad
tar -tzf ~/backups/agente_autonomo/backup_20251227_181505.tar.gz > /dev/null && \
  echo "✅ Backup válido" || echo "❌ Backup corrupto"
```

---

**Última actualización:** 2025-12-27 18:15
