# 🚀 Scripts de Control del Sistema

Scripts para gestionar el ciclo de vida del Agente Autónomo.

---

## 📋 Scripts Disponibles

### 1. `start_all.sh` - Iniciar Sistema Completo

Inicia **Frontend** y **Backend** simultáneamente.

**Uso:**
```bash
./start_all.sh
```

**Características:**
- ✅ Verifica y libera puertos automáticamente
- ✅ Inicia Backend (puerto 8000)
- ✅ Inicia Frontend (puerto 3000)
- ✅ Espera a que ambos servicios estén listos
- ✅ Muestra logs en tiempo real
- ✅ Cleanup automático con Ctrl+C

**Salida:**
```
🚀 Iniciando Sistema Completo - Agente Autónomo
================================================

🔍 Verificando puertos...
✅ Puertos libres

🔧 Iniciando Backend API...
   PID: 12345
   ✅ Backend listo en http://localhost:8000

🌐 Iniciando Frontend Web Server...
   PID: 12346
   ✅ Frontend listo en http://localhost:3000

================================================
✅ Sistema iniciado correctamente

📍 URLs:
   Frontend: http://localhost:3000
   Backend:  http://localhost:8000
   API Docs: http://localhost:8000/docs

📋 Logs:
   Backend:  logs/backend.log
   Frontend: logs/frontend.log

💡 Presiona Ctrl+C para detener todos los servicios
================================================
```

---

### 2. `stop_all.sh` - Detener Sistema Completo

Detiene todos los servicios de forma limpia.

**Uso:**
```bash
./stop_all.sh
```

**Características:**
- ✅ Detiene Backend (puerto 8000)
- ✅ Detiene Frontend (puerto 3000)
- ✅ Limpia procesos residuales
- ✅ Confirmación de cada paso

**Salida:**
```
🛑 Deteniendo Sistema Completo - Agente Autónomo
================================================
Deteniendo Backend (puerto 8000)...
✅ Backend detenido

Deteniendo Frontend (puerto 3000)...
✅ Frontend detenido

Limpiando procesos residuales...
✅ Limpieza completada

================================================
✅ Todos los servicios detenidos
================================================
```

---

### 3. `start_server.sh` - Solo Backend

Inicia únicamente el servidor Backend.

**Uso:**
```bash
./start_server.sh
```

---

### 4. `start_frontend.sh` - Solo Frontend

Inicia únicamente el servidor Frontend.

**Uso:**
```bash
./start_frontend.sh
```

---

### 5. `restart_server.sh` - Reiniciar Backend

Detiene y reinicia el Backend.

**Uso:**
```bash
./restart_server.sh
```

---

### 6. `stop_server.sh` - Detener Backend

Detiene únicamente el Backend.

**Uso:**
```bash
./stop_server.sh
```

---

## 🔧 Solución de Problemas

### Puerto ocupado

Si ves errores de "Address already in use":

```bash
# Opción 1: Usar stop_all.sh
./stop_all.sh

# Opción 2: Manual
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

### Backend no inicia

```bash
# Ver logs
tail -f logs/backend.log

# Verificar dependencias
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend no carga

```bash
# Ver logs
tail -f logs/frontend.log

# Verificar archivos
ls -la frontend/
```

---

## 📊 Monitoreo

### Ver logs en tiempo real

```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Ambos
tail -f logs/*.log
```

### Verificar estado

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Puertos
lsof -i:8000
lsof -i:3000
```

---

## 🚀 Flujo de Trabajo Recomendado

### Desarrollo Normal

```bash
# 1. Iniciar todo
./start_all.sh

# 2. Trabajar...
# (El sistema recarga automáticamente los cambios)

# 3. Detener todo
Ctrl+C  # o ./stop_all.sh
```

### Solo Backend

```bash
# Si solo necesitas el backend
./start_server.sh
```

### Solo Frontend

```bash
# Si solo necesitas el frontend
./start_frontend.sh
```

### Reiniciar Backend

```bash
# Después de cambios en el código Python
./restart_server.sh
```

---

## 📁 Estructura de Logs

```
logs/
├── backend.log   # Logs del servidor FastAPI
└── frontend.log  # Logs del servidor HTTP
```

**Nota:** Los logs se crean automáticamente al usar `start_all.sh`

---

## ⚙️ Variables de Entorno

Los scripts usan las siguientes configuraciones:

- **Backend Port:** 8000
- **Frontend Port:** 3000
- **Backend Host:** 0.0.0.0
- **Frontend Dir:** frontend/

Para cambiar, edita los scripts correspondientes.

---

## 🔒 Permisos

Asegúrate de que los scripts tengan permisos de ejecución:

```bash
chmod +x start_all.sh
chmod +x stop_all.sh
chmod +x start_server.sh
chmod +x start_frontend.sh
chmod +x restart_server.sh
chmod +x stop_server.sh
```

---

## 📝 Notas

- `start_all.sh` usa `trap` para cleanup automático
- Los logs se rotan automáticamente (sobrescriben en cada inicio)
- Ctrl+C en `start_all.sh` detiene ambos servicios
- Los scripts verifican puertos antes de iniciar

---

**Última actualización:** 2025-12-26
