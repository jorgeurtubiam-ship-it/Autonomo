# 🚀 Guía de Acceso - Agente Autónomo

## 📍 URLs de Acceso

### Frontend (Interfaz Web)
```
Archivo Local: /Users/lordzero1/IA_LoRdZeRo/auto/frontend/index.html
```

**Abrir en navegador:**
```bash
# Opción 1: Abrir directamente
open /Users/lordzero1/IA_LoRdZeRo/auto/frontend/index.html

# Opción 2: Con servidor local
cd /Users/lordzero1/IA_LoRdZeRo/auto/frontend
python3 -m http.server 8080
# Luego abre: http://localhost:8080
```

### Backend API
```
API Base: http://localhost:8000
Documentación Swagger: http://localhost:8000/docs
Documentación ReDoc: http://localhost:8000/redoc
Health Check: http://localhost:8000/health
```

## 🔓 Autenticación

**NO requiere autenticación** (por ahora)
- ✅ Sin usuario/contraseña
- ✅ Sin tokens
- ✅ Acceso directo

## 🧪 Pruebas con curl

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "service": "agent-api",
  "version": "1.0.0",
  "uptime_seconds": 123.45
}
```

### 2. Listar Tools
```bash
curl http://localhost:8000/api/tools
```

**Respuesta:** Lista de 13 tools disponibles

### 3. Obtener Configuración
```bash
curl http://localhost:8000/api/config
```

**Respuesta:**
```json
{
  "llm_provider": "ollama",
  "model": "llama3.2:latest",
  "autonomy_level": "semi",
  "tools_count": 13
}
```

### 4. Listar Conversaciones
```bash
curl http://localhost:8000/api/conversations
```

### 5. Enviar Mensaje (Simple)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola",
    "conversation_id": "test_curl"
  }'
```

**Nota:** Este puede tardar porque Ollama procesa el mensaje.

### 6. Ver Historial
```bash
curl http://localhost:8000/api/chat/test_curl/history
```

## 🌐 Acceso desde Navegador

### Swagger UI (Recomendado)
```
http://localhost:8000/docs
```

**Características:**
- ✅ Interfaz visual para probar endpoints
- ✅ Documentación automática
- ✅ Prueba directa desde el navegador
- ✅ Ejemplos de requests/responses

### ReDoc
```
http://localhost:8000/redoc
```

**Características:**
- ✅ Documentación más detallada
- ✅ Mejor para leer
- ✅ Exportable

## 🎨 Frontend Web

### Acceso
1. Abre `frontend/index.html` en tu navegador
2. O usa: `open /Users/lordzero1/IA_LoRdZeRo/auto/frontend/index.html`

### Características
- 💬 Chat en tiempo real
- 🔧 Visualización de tools
- 📝 Historial de conversaciones
- 🎨 Dark theme moderno
- 📱 Responsive

### Sin Autenticación
- No necesitas login
- Acceso directo
- Todas las funciones disponibles

## 🔧 WebSocket

### Conectar con JavaScript
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/mi_conversacion');

ws.onopen = () => console.log('Conectado');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evento:', data);
};

ws.send(JSON.stringify({
  message: 'Hola desde WebSocket'
}));
```

### Conectar con Python
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat/mi_conversacion"
    async with websockets.connect(uri) as ws:
        # Recibir confirmación
        msg = await ws.recv()
        print(json.loads(msg))
        
        # Enviar mensaje
        await ws.send(json.dumps({"message": "Hola"}))
        
        # Recibir respuestas
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            print(data)
            if data['type'] == 'done':
                break

asyncio.run(chat())
```

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción | Requiere Auth |
|----------|--------|-------------|---------------|
| `/` | GET | Info del API | ❌ |
| `/health` | GET | Health check | ❌ |
| `/docs` | GET | Swagger UI | ❌ |
| `/api/tools` | GET | Listar tools | ❌ |
| `/api/tools/{name}` | GET | Detalle de tool | ❌ |
| `/api/config` | GET | Configuración | ❌ |
| `/api/config` | PUT | Actualizar config | ❌ |
| `/api/conversations` | GET | Listar conversaciones | ❌ |
| `/api/conversations/{id}` | GET | Detalle conversación | ❌ |
| `/api/conversations/{id}` | DELETE | Eliminar conversación | ❌ |
| `/api/chat` | POST | Enviar mensaje | ❌ |
| `/api/chat/{id}/history` | GET | Historial | ❌ |
| `/ws/chat/{id}` | WS | WebSocket streaming | ❌ |

## 🎯 Ejemplos Rápidos

### Ver en Navegador
```bash
# 1. Abrir Swagger UI
open http://localhost:8000/docs

# 2. Abrir Frontend
open /Users/lordzero1/IA_LoRdZeRo/auto/frontend/index.html
```

### Probar con curl
```bash
# Health check
curl http://localhost:8000/health

# Listar tools
curl http://localhost:8000/api/tools | python3 -m json.tool

# Ver conversaciones
curl http://localhost:8000/api/conversations | python3 -m json.tool
```

## 🔒 Seguridad (Futuro)

**Actualmente NO implementado:**
- ❌ JWT tokens
- ❌ API keys
- ❌ Rate limiting
- ❌ User authentication

**Para producción, se debería agregar:**
- ✅ JWT authentication
- ✅ API keys
- ✅ Rate limiting
- ✅ HTTPS
- ✅ CORS restrictivo

## 📝 Notas

1. **Backend debe estar corriendo** en puerto 8000
2. **Sin autenticación** - Acceso abierto
3. **CORS habilitado** para todos los orígenes
4. **WebSocket** disponible para streaming
5. **Swagger UI** para pruebas interactivas

## 🚀 Inicio Rápido

```bash
# 1. Iniciar backend (si no está corriendo)
./start_server.sh

# 2. Abrir frontend
open frontend/index.html

# 3. O abrir Swagger UI
open http://localhost:8000/docs
```

¡Listo para usar! 🎉
