# Backend API - Guía Completa

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
# Opción 1: Con pip (requiere entorno virtual)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Opción 2: Con pip user
pip install --user fastapi uvicorn[standard] websockets

# Opción 3: Con pipx (recomendado para macOS)
brew install pipx
pipx install fastapi
pipx install uvicorn
```

### 2. Iniciar Servidor

```bash
cd backend/api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 Endpoints Disponibles

### Chat

#### POST /api/chat
Envía un mensaje al agente.

**Request:**
```json
{
  "message": "Crea un archivo test.txt con 'Hola'",
  "conversation_id": "conv_123",
  "stream": false
}
```

**Response:**
```json
{
  "conversation_id": "conv_123",
  "message": "Archivo creado exitosamente",
  "tool_calls": [
    {
      "id": "call_1",
      "name": "write_file",
      "arguments": {"path": "test.txt", "content": "Hola"}
    }
  ],
  "iterations": 2
}
```

#### GET /api/chat/{conversation_id}/history
Obtiene el historial de una conversación.

**Response:**
```json
{
  "conversation_id": "conv_123",
  "messages": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ],
  "total": 2
}
```

### Tools

#### GET /api/tools
Lista todos los tools disponibles.

**Response:**
```json
{
  "tools": [
    {
      "name": "write_file",
      "description": "Crea o escribe un archivo",
      "category": "file",
      "parameters": {...}
    }
  ],
  "total": 13
}
```

#### GET /api/tools/{tool_name}
Obtiene información de un tool específico.

### Config

#### GET /api/config
Obtiene la configuración actual.

**Response:**
```json
{
  "llm_provider": "ollama",
  "model": "llama3.2:latest",
  "autonomy_level": "semi",
  "temperature": 0.7,
  "max_tokens": 4000,
  "tools_count": 13
}
```

#### PUT /api/config
Actualiza la configuración.

**Request:**
```json
{
  "llm_provider": "deepseek",
  "model": "deepseek-chat",
  "autonomy_level": "full"
}
```

### Health

#### GET /health
Health check del servicio.

**Response:**
```json
{
  "status": "healthy",
  "service": "agent-api",
  "version": "1.0.0",
  "uptime_seconds": 123.45
}
```

## 💻 Ejemplos de Uso

### Con curl

```bash
# Enviar mensaje
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Lista los archivos en el directorio actual",
    "conversation_id": "test_001"
  }'

# Listar tools
curl http://localhost:8000/api/tools

# Obtener configuración
curl http://localhost:8000/api/config
```

### Con Python requests

```python
import requests

# Enviar mensaje
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Crea un archivo hello.txt",
        "conversation_id": "python_test"
    }
)
print(response.json())

# Listar tools
tools = requests.get("http://localhost:8000/api/tools")
print(f"Tools disponibles: {tools.json()['total']}")
```

### Con JavaScript fetch

```javascript
// Enviar mensaje
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: 'Lista archivos',
    conversation_id: 'js_test'
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

## 🏗️ Arquitectura

```
Cliente (Frontend/CLI)
    ↓
FastAPI (main.py)
    ↓
Routes (chat, tools, config)
    ↓
Dependencies (get_agent)
    ↓
AgentCore (Singleton)
    ↓
LLM Provider + Tools
```

## 🔧 Configuración

### Variables de Entorno

```bash
# LLM API Keys (opcional según proveedor)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DEEPSEEK_API_KEY="sk-..."

# Configuración del servidor
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### Archivo .env

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Testing

```bash
# Test de estructura
python3 tests/test_api_structure.py

# Test con pytest (cuando FastAPI esté instalado)
pytest tests/test_api_*.py -v
```

## 📊 Monitoreo

### Logs

El servidor muestra logs en tiempo real:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Métricas

- Uptime: `/health`
- Tools disponibles: `/api/tools`
- Configuración: `/api/config`

## 🚨 Troubleshooting

### Error: "No module named 'fastapi'"

```bash
pip install --user fastapi uvicorn[standard]
```

### Error: "Address already in use"

```bash
# Cambiar puerto
python3 -m uvicorn main:app --port 8001
```

### Error: "No module named 'agent'"

```bash
# Ejecutar desde el directorio correcto
cd backend/api
python3 -m uvicorn main:app --reload
```

## 🔐 Seguridad (TODO)

- [ ] Autenticación JWT
- [ ] Rate limiting
- [ ] CORS configurado para producción
- [ ] Validación de inputs
- [ ] Sanitización de outputs

## 📝 Próximas Características

- [ ] WebSocket para streaming
- [ ] Base de datos para persistencia
- [ ] Sistema de usuarios
- [ ] Métricas y analytics
- [ ] Cache de respuestas
