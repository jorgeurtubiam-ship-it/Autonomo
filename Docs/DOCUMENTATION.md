# 🤖 Agente Autónomo - Documentación Completa

**Versión:** 2.0.0  
**Última actualización:** 2025-12-27  
**Estado:** ✅ Producción

---

## 📋 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características](#-características)
3. [Arquitectura](#-arquitectura)
4. [Instalación](#-instalación)
5. [Configuración](#-configuración)
6. [Uso](#-uso)
7. [API Reference](#-api-reference)
8. [Desarrollo](#-desarrollo)
9. [Deployment](#-deployment)
10. [Troubleshooting](#-troubleshooting)

---

## 🎯 Descripción General

**Agente Autónomo** es un sistema de IA conversacional avanzado que combina:
- 🧠 **Múltiples LLM Providers** (DeepSeek, OpenAI, Anthropic, Ollama)
- 🛠️ **15+ Herramientas** para gestión de archivos, comandos y Git
- 💬 **Interfaz Web** moderna con WebSocket en tiempo real
- 💾 **Persistencia** de conversaciones en SQLite
- 🔄 **Hot-swap** de providers sin reiniciar

### Casos de Uso

- **Desarrollo de Software:** Crear, modificar y gestionar código
- **DevOps:** Ejecutar comandos, gestionar infraestructura
- **Automatización:** Scripts, tareas repetitivas, workflows
- **Asistente Personal:** Gestión de archivos, búsquedas, análisis

---

## ✨ Características

### Backend (FastAPI + Python)

- ✅ **Multi-LLM Support**
  - DeepSeek (recomendado, económico)
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude 3.5 Sonnet)
  - Ollama (local, gratis)

- ✅ **REST API + WebSocket**
  - Endpoints RESTful para configuración
  - WebSocket para streaming en tiempo real
  - CORS configurado para desarrollo

- ✅ **15+ Tools**
  - File operations (read, write, search, delete)
  - Command execution (shell, scripts)
  - Git operations (status, diff, commit, log)

- ✅ **Persistencia**
  - SQLite para conversaciones
  - API keys encriptadas
  - Historial completo de mensajes

### Frontend (HTML + CSS + JavaScript)

- ✅ **Interfaz Moderna**
  - Diseño dark mode profesional
  - Glassmorphism effects
  - Responsive design

- ✅ **Features**
  - Chat en tiempo real
  - Historial de conversaciones
  - Selector de provider/modelo
  - Configuración de API keys
  - Indicadores de estado

- ✅ **UX**
  - Markdown rendering
  - Code syntax highlighting
  - Tool execution feedback
  - Auto-scroll

---

## 🏗️ Arquitectura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 3000)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  index.html  │  │   app.js     │  │  style.css   │  │
│  │  (UI)        │  │  (Logic)     │  │  (Design)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                    HTTP + WebSocket
                           │
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (Port 8000)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │              FastAPI Application                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │   Routes   │  │ WebSocket  │  │   Models   │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Agent Core                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ LLM        │  │  Context   │  │   Tools    │  │  │
│  │  │ Provider   │  │  Manager   │  │  Registry  │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│                           │                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Storage Layer                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  │
│  │  │ SQLite DB  │  │  API Keys  │  │   Files    │  │  │
│  │  └────────────┘  └────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Mensajes

```
Usuario → Frontend → WebSocket → Backend → Agent Core
                                              ↓
                                         LLM Provider
                                              ↓
                                         Tool Execution
                                              ↓
                                         Response Stream
                                              ↓
Frontend ← WebSocket ← Backend ← Agent Core
```

### Estructura de Directorios

```
auto/
├── backend/                    # Backend Python
│   ├── agent/                  # Core del agente
│   │   ├── __init__.py
│   │   ├── core.py            # AgentCore principal
│   │   ├── llm_provider.py    # Multi-LLM abstraction
│   │   ├── context.py         # Context manager
│   │   ├── config.py          # Configuración
│   │   └── prompts.py         # System prompts
│   ├── api/                   # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py            # App principal
│   │   ├── models.py          # Pydantic models
│   │   ├── dependencies.py    # DI containers
│   │   ├── routes/            # API endpoints
│   │   │   ├── chat.py        # Chat endpoints
│   │   │   ├── config.py      # Config endpoints
│   │   │   └── conversations.py
│   │   └── websocket/         # WebSocket handlers
│   ├── storage/               # Persistencia
│   │   ├── __init__.py
│   │   ├── conversation_storage.py
│   │   └── models.py
│   └── tools/                 # Herramientas
│       ├── __init__.py
│       ├── file_tools.py      # File operations
│       ├── command_tools.py   # Shell commands
│       └── git_tools.py       # Git operations
├── frontend/                  # Frontend web
│   ├── index.html            # UI principal
│   ├── app.js                # Lógica JavaScript
│   ├── style.css             # Estilos
│   └── README.md
├── Docs/                     # Documentación
│   ├── architecture/
│   ├── api/
│   └── development/
├── scripts/                  # Scripts de utilidad
├── tests/                    # Tests
├── logs/                     # Logs de aplicación
├── requirements.txt          # Dependencias Python
├── start_all.sh             # Iniciar todo
├── stop_all.sh              # Detener todo
└── README.md                # Este archivo
```

---

## 🚀 Instalación

### Requisitos Previos

- **Python:** 3.10 o superior
- **pip:** Gestor de paquetes Python
- **Git:** Para clonar el repositorio
- **Opcional:** Ollama (para LLM local)

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/auto.git
cd auto
```

### Paso 2: Crear Entorno Virtual

```bash
# Crear venv
python3 -m venv venv

# Activar (macOS/Linux)
source venv/bin/activate

# Activar (Windows)
venv\\Scripts\\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar API Keys

Elige uno de los siguientes providers:

#### Opción A: DeepSeek (Recomendado)

```bash
export DEEPSEEK_API_KEY="sk-..."
```

O guárdalo en `.env`:

```bash
echo "DEEPSEEK_API_KEY=sk-..." > .env
```

#### Opción B: OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

#### Opción C: Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

#### Opción D: Ollama (Local, Gratis)

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2:latest

# Iniciar servidor
ollama serve
```

### Paso 5: Iniciar Aplicación

```bash
# Opción 1: Iniciar todo (Backend + Frontend)
./start_all.sh

# Opción 2: Solo Backend
./start_server.sh

# Opción 3: Solo Frontend
./start_frontend.sh
```

### Verificar Instalación

```bash
# Backend
curl http://localhost:8000/health

# Frontend
open http://localhost:3000
```

---

## ⚙️ Configuración

### Configuración del Backend

El backend se configura mediante:
1. Variables de entorno
2. Archivo `.env`
3. API REST (en tiempo de ejecución)

#### Variables de Entorno

```bash
# LLM Provider
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=sqlite:///~/.agent_data/conversations/agent.db

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true
```

#### Cambiar Provider en Tiempo Real

```bash
# Via API
curl -X PUT http://localhost:8000/api/config/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "llm_provider": "deepseek",
    "model": "deepseek-chat"
  }'
```

O desde el frontend:
1. Click en selector "Provider"
2. Seleccionar DeepSeek/OpenAI/Anthropic/Ollama
3. Seleccionar modelo
4. Los cambios se aplican inmediatamente

### Configuración del Frontend

El frontend se configura en `frontend/app.js`:

```javascript
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';
```

Para producción, cambiar a tu dominio:

```javascript
const API_URL = 'https://api.tudominio.com';
const WS_URL = 'wss://api.tudominio.com';
```

### Base de Datos

La base de datos SQLite se crea automáticamente en:

```
~/.agent_data/conversations/agent.db
```

**Tablas:**
- `conversations` - Conversaciones
- `messages` - Mensajes
- `api_keys` - API keys (encriptadas)

**Backup:**

```bash
# Backup manual
cp ~/.agent_data/conversations/agent.db backup_$(date +%Y%m%d).db

# Ver datos
sqlite3 ~/.agent_data/conversations/agent.db "SELECT * FROM conversations;"
```

---

## 💻 Uso

### Interfaz Web

1. **Abrir navegador:** http://localhost:3000

2. **Configurar API Key (primera vez):**
   - Click en botón 🔑 "API Keys"
   - Ingresar API key de DeepSeek/OpenAI/Anthropic
   - Click "💾 Guardar"

3. **Iniciar conversación:**
   - Click "+ Nueva Conversación"
   - Escribir mensaje
   - Presionar Enter o click "Enviar"

4. **Cambiar provider:**
   - Usar dropdown "Provider"
   - Seleccionar modelo
   - Los cambios se aplican automáticamente

### Ejemplos de Comandos

#### Gestión de Archivos

```
"Crea un archivo hello.py con un script que imprima 'Hola Mundo'"
"Lee el contenido de README.md"
"Busca todos los archivos .js en el proyecto"
"Elimina el archivo temp.txt"
```

#### Comandos Shell

```
"Ejecuta 'ls -la' en el directorio actual"
"Instala el paquete requests con pip"
"Lista los procesos de Python corriendo"
"Ejecuta npm install en frontend/"
```

#### Git Operations

```
"Muestra el estado del repositorio Git"
"Haz un commit con mensaje 'feat: add feature'"
"Muestra los últimos 5 commits"
"Muestra los cambios en app.js"
```

#### Desarrollo

```
"Crea un servidor Express básico en Node.js"
"Escribe tests para la función fibonacci"
"Refactoriza el código en utils.py"
"Documenta la función process_message"
```

### API Programática

```python
import asyncio
from backend.agent import AgentCore, AgentConfig, create_llm_provider
from backend.tools import get_all_tools

async def main():
    # Crear agente
    llm = create_llm_provider("deepseek")
    config = AgentConfig(autonomy_level="semi")
    agent = AgentCore(llm, config)
    
    # Registrar tools
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    # Procesar mensaje
    async for event in agent.process_message(
        "Crea un archivo test.txt",
        "conv_001"
    ):
        if event["type"] == "message":
            print(event["content"])
        elif event["type"] == "tool_call":
            print(f"Ejecutando: {event['tool']}")

asyncio.run(main())
```

---

## 📡 API Reference

### REST Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "agent-api",
  "version": "1.0.0",
  "uptime_seconds": 123.45
}
```

#### Get Configuration

```http
GET /api/config/
```

**Response:**
```json
{
  "llm_provider": "deepseek",
  "model": "deepseek-chat",
  "autonomy_level": "semi",
  "temperature": 0.7,
  "max_tokens": 4000,
  "tools_count": 15
}
```

#### Update Configuration

```http
PUT /api/config/
Content-Type: application/json

{
  "llm_provider": "deepseek",
  "model": "deepseek-chat",
  "api_keys": {
    "deepseek": "sk-..."
  }
}
```

#### List Conversations

```http
GET /api/conversations/
```

**Response:**
```json
[
  {
    "id": "conv_123",
    "title": "Nueva Conversación",
    "created_at": "2025-12-27T00:00:00Z",
    "updated_at": "2025-12-27T01:00:00Z",
    "message_count": 5
  }
]
```

#### Get Conversation History

```http
GET /api/chat/{conversation_id}/history
```

**Response:**
```json
{
  "conversation_id": "conv_123",
  "messages": [
    {
      "role": "user",
      "content": "Hola",
      "created_at": "2025-12-27T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "¡Hola! ¿En qué puedo ayudarte?",
      "created_at": "2025-12-27T00:00:01Z"
    }
  ]
}
```

#### Delete Conversation

```http
DELETE /api/conversations/{conversation_id}
```

### WebSocket

#### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/conv_123');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};
```

#### Send Message

```javascript
ws.send(JSON.stringify({
  message: "Hola, ¿cómo estás?"
}));
```

#### Message Types

**Connected:**
```json
{
  "type": "connected"
}
```

**Thinking:**
```json
{
  "type": "thinking"
}
```

**Tool Call:**
```json
{
  "type": "tool_call",
  "tool": "read_file",
  "arguments": {"path": "README.md"}
}
```

**Tool Result:**
```json
{
  "type": "tool_result",
  "tool": "read_file",
  "result": "File content..."
}
```

**Message Chunk (Streaming):**
```json
{
  "type": "message_chunk",
  "content": "Hola"
}
```

**Done:**
```json
{
  "type": "done"
}
```

**Error:**
```json
{
  "type": "error",
  "error": "Error message"
}
```

---

## 🛠️ Desarrollo

### Setup de Desarrollo

```bash
# Clonar repo
git clone https://github.com/tu-usuario/auto.git
cd auto

# Crear venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock black flake8

# Instalar pre-commit hooks
pre-commit install
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_agent.py

# Con coverage
pytest --cov=backend --cov-report=html
```

### Crear Tool Personalizado

```python
# backend/tools/custom_tool.py
from typing import Dict, Any

async def my_custom_tool(param1: str, param2: int) -> Dict[str, Any]:
    \"\"\"
    Descripción de la herramienta.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
    
    Returns:
        Dict con el resultado
    \"\"\"
    # Tu lógica aquí
    result = f"Procesado: {param1} con {param2}"
    
    return {
        "success": True,
        "result": result
    }

# Registrar en backend/tools/__init__.py
from .custom_tool import my_custom_tool

def get_all_tools():
    return [
        # ... tools existentes
        my_custom_tool,
    ]
```

### Code Style

```bash
# Format code
black backend/ tests/

# Lint
flake8 backend/ tests/

# Type check
mypy backend/
```

---

## 🚀 Deployment

### Producción con Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 8000 3000

CMD ["./start_all.sh"]
```

```bash
# Build
docker build -t agente-autonomo .

# Run
docker run -p 8000:8000 -p 3000:3000 \\
  -e DEEPSEEK_API_KEY=sk-... \\
  agente-autonomo
```

### Producción con Systemd

```ini
# /etc/systemd/system/agente-backend.service
[Unit]
Description=Agente Autónomo Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/agente-autonomo
Environment="DEEPSEEK_API_KEY=sk-..."
ExecStart=/opt/agente-autonomo/venv/bin/python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable agente-backend
sudo systemctl start agente-backend
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Troubleshooting

### Backend no inicia

**Problema:** `Address already in use`

**Solución:**
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# O usar script
./stop_all.sh
```

### WebSocket se desconecta

**Problema:** WebSocket cierra inmediatamente

**Solución:**
- Verificar que backend esté corriendo
- Revisar logs: `tail -f logs/backend.log`
- Verificar CORS en `backend/api/main.py`

### AI no responde

**Problema:** Mensaje enviado pero sin respuesta

**Solución:**
1. Verificar provider configurado:
   ```bash
   curl http://localhost:8000/api/config/
   ```

2. Verificar API key:
   ```bash
   sqlite3 ~/.agent_data/conversations/agent.db "SELECT * FROM api_keys;"
   ```

3. Ver logs de error:
   ```bash
   tail -100 logs/backend.log | grep -i error
   ```

### Error de LLM

**Problema:** `Error en llamada al LLM`

**Solución:**
- Verificar API key válida
- Verificar saldo/créditos
- Si usa Ollama, verificar que esté corriendo:
  ```bash
  ollama list
  ps aux | grep ollama
  ```

---

## 📚 Recursos Adicionales

- **Documentación Completa:** [Docs/](Docs/)
- **Ejemplos:** [examples/](examples/)
- **Tests:** [tests/](tests/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'feat: add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

---

## 💬 Soporte

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/auto/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tu-usuario/auto/discussions)
- **Email:** soporte@tudominio.com

---

**Hecho con ❤️ por el equipo de Agente Autónomo**
