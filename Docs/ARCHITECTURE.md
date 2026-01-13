# 🏗️ Arquitectura del Sistema

## Visión General

El Agente Autónomo está construido con una arquitectura modular de 3 capas:

1. **Capa de Presentación** (Frontend)
2. **Capa de Aplicación** (Backend API)
3. **Capa de Dominio** (Agent Core + Tools)

---

## Componentes Principales

### 1. Frontend (Presentation Layer)

**Tecnologías:**
- HTML5
- CSS3 (Glassmorphism, Dark Mode)
- Vanilla JavaScript (ES6+)

**Responsabilidades:**
- Renderizar interfaz de usuario
- Gestionar estado local (conversación actual)
- Comunicación WebSocket con backend
- Formatear mensajes (Markdown)
- **Modo Terminal Live:** Renderizado de comandos en consola profesional
- **Thinking State:** Indicador visual de procesamiento animado

**Archivos:**
```
frontend/
├── index.html      # Estructura HTML
├── app.js          # Lógica de aplicación
└── style.css       # Estilos y diseño
```

**Flujo de Datos:**
```
User Input → app.js → WebSocket → Backend
Backend → WebSocket → app.js → DOM Update → User
```

---

### 2. Backend API (Application Layer)

**Tecnologías:**
- FastAPI (Python 3.10+)
- Uvicorn (ASGI server)
- WebSockets
- Pydantic (validation)

**Responsabilidades:**
- Exponer API REST
- Gestionar conexiones WebSocket
- Validar requests
- Orquestar Agent Core
- Persistir datos

**Estructura:**
```
backend/api/
├── main.py              # FastAPI app
├── models.py            # Pydantic models
├── dependencies.py      # Dependency injection
├── routes/
│   ├── chat.py         # Chat endpoints
│   ├── config.py       # Configuration
│   └── conversations.py # Conversation management
└── websocket/
    └── chat_ws.py      # WebSocket handlers
```

**Endpoints:**
- `GET /health` - Health check
- `GET /api/config/` - Get configuration
- `PUT /api/config/` - Update configuration
- `GET /api/conversations/` - List conversations
- `GET /api/chat/{id}/history` - Get history
- `DELETE /api/conversations/{id}` - Delete conversation
- `WS /ws/chat/{id}` - WebSocket chat

---

### 3. Agent Core (Domain Layer)

**Tecnologías:**
- Python 3.10+
- Async/await
- Type hints

**Responsabilidades:**
- Procesar mensajes del usuario
- Gestionar contexto de conversación
- Interactuar con LLM
- Streaming de respuestas
- **Self-Healing Protocol:** Recuperación autónoma ante errores de ejecución.

**Estructura:**
```
backend/agent/
├── core.py           # AgentCore (motor principal)
├── llm_provider.py   # Multi-LLM abstraction
├── context.py        # Context manager
├── config.py         # Agent configuration
└── prompts.py        # System prompts
```

**Ciclo de Procesamiento:**
```
1. Recibir mensaje
2. Cargar contexto de conversación
3. Construir prompt con tools disponibles
4. Llamar LLM
5. Parsear respuesta (texto + tool calls)
   - **Fallback Parsing:** Extracción de JSON del contenido de texto si no hay tool calls nativos.
   - **Hallucination Filter:** Detección y filtrado de resultados de herramientas predecidos por el LLM.
6. Ejecutar tools si es necesario
7. **Self-Healing Check:** Si la herramienta devuelve un error, el agente puede decidir investigar la solución mediante el navegador.
8. Enviar resultados al LLM
9. Repetir hasta respuesta final
10. Guardar en contexto
```

---

### 4. Tools (Domain Layer)

**Responsabilidades:**
- Ejecutar operaciones del sistema
- Validar parámetros
- Manejar errores
- Retornar resultados estructurados

**Categorías:**

#### File Tools
```python
- read_file(path)
- write_file(path, content)
- list_directory(path)
- search_files(pattern, directory)
- delete_file(path)
- get_file_info(path)
```

#### Command Tools
```python
- execute_command(command, cwd, timeout)
- run_script(script_path, args)
- install_package(package, manager)
```

#### Git Tools
```python
- git_status(repo_path)
- git_diff(repo_path, file)
- git_commit(repo_path, message)
- git_log(repo_path, limit)
```

**Estructura de Tool:**
```python
async def tool_name(param1: str, param2: int) -> Dict[str, Any]:
    \"\"\"
    Tool description for LLM.
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Dict with result
    \"\"\"
    # Validation
    if not param1:
        return {\"success\": False, \"error\": \"param1 required\"}
    
    # Execution
    try:
        result = do_something(param1, param2)
        return {\"success\": True, \"result\": result}
    except Exception as e:
        return {\"success\": False, \"error\": str(e)}
```

---

### 5. Storage Layer

**Tecnologías:**
- SQLite
- SQLAlchemy (ORM)

**Responsabilidades:**
- Persistir conversaciones
- Guardar mensajes
- Almacenar API keys
- Gestionar historial

**Estructura:**
```
backend/storage/
├── conversation_storage.py  # Storage implementation
└── models.py                # SQLAlchemy models
```

**Schema:**
```sql
-- Conversations
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    message_count INTEGER
);

-- Messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT,
    role TEXT,
    content TEXT,
    tool_calls TEXT,  -- JSON
    created_at TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- API Keys
CREATE TABLE api_keys (
    provider TEXT PRIMARY KEY,
    api_key TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Patrones de Diseño

### 1. Dependency Injection

```python
# backend/api/dependencies.py
def get_agent() -> AgentCore:
    \"\"\"Singleton agent instance\"\"\"
    if not hasattr(get_agent, \"instance\"):
        llm = create_llm_provider(\"deepseek\")
        get_agent.instance = AgentCore(llm, AgentConfig())
    return get_agent.instance

# Usage in routes
@router.get(\"/config/\")
async def get_config(agent: AgentCore = Depends(get_agent)):
    return agent.config
```

### 2. Strategy Pattern (LLM Providers)

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages, tools):
        pass

class DeepSeekProvider(LLMProvider):
    async def generate(self, messages, tools):
        # DeepSeek implementation
        pass

class OpenAIProvider(LLMProvider):
    async def generate(self, messages, tools):
        # OpenAI implementation
        pass
```

### 3. Observer Pattern (WebSocket Events)

```python
async def process_message(message, conversation_id):
    # Emit events
    await websocket.send_json({"type": "thinking"})
    await websocket.send_json({"type": "tool_call", "name": "execute_command", "arguments": {"command": "ls"}})
    await websocket.send_json({"type": "message_chunk", "content": "..."})
    await websocket.send_json({"type": "done"})
```

### 4. Circuit Breaker / Fallback (Tool Extraction)

El sistema utiliza un patrón de extracción multicapa para robustez con modelos locales (Ollama):
1. **Nativo:** Intenta obtener `tool_calls` del campo oficial de la API.
2. **Regex Fallback:** Si falla, busca bloques JSON en el texto que coincidan con el esquema de herramientas. Utiliza un algoritmo de conteo de llaves balanceadas para soportar objetos anidados complejos.
3. **Fuzzy Parsing:** Limpieza de caracteres y markdown antes del parseo JSON.

### 5. Self-Healing Research Loop

Cuando un modelo (como Ollama) genera una sintaxis incorrecta para una herramienta:
1. El backend captura el error de ejecución.
2. El sistema de instrucciones provee al agente la capacidad de usar el tool `browser` con la acción `search`.
3. El agente busca documentación u ejemplos del comando fallido.
4. El agente genera un nuevo "Plan" basado en la información encontrada y reintenta la acción.

---

---

## Flujos de Datos

### Flujo de Chat (WebSocket)

```
┌─────────┐                ┌──────────┐                ┌────────────┐
│ Frontend│                │  Backend │                │ Agent Core │
└────┬────┘                └────┬─────┘                └─────┬──────┘
     │                          │                            │
     │ 1. Connect WS            │                            │
     ├─────────────────────────\u003e│                            │
     │                          │                            │
     │ 2. {type: \"connected\"}   │                            │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
     │ 3. Send message          │                            │
     ├─────────────────────────\u003e│                            │
     │                          │ 4. Process message         │
     │                          ├───────────────────────────\u003e│
     │                          │                            │
     │ 5. {type: \"thinking\"}    │                            │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
     │                          │ 6. Call LLM                │
     │                          │\u003c───────────────────────────┤
     │                          │                            │
     │ 7. {type: \"tool_call\"}   │                            │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
     │                          │ 8. Execute tool            │
     │                          │\u003c───────────────────────────┤
     │                          │                            │
     │ 9. {type: \"message_chunk\"}│                           │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
     │ 10. {type: \"done\"}        │                            │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
```

### Flujo de Configuración (REST)

```
┌─────────┐                ┌──────────┐                ┌────────────┐
│ Frontend│                │  Backend │                │  Storage   │
└────┬────┘                └────┬─────┘                └─────┬──────┘
     │                          │                            │
     │ 1. PUT /api/config/      │                            │
     ├─────────────────────────\u003e│                            │
     │                          │                            │
     │                          │ 2. Save API key            │
     │                          ├───────────────────────────\u003e│
     │                          │                            │
     │                          │ 3. Reconfigure agent       │
     │                          │                            │
     │                          │ 4. Return config           │
     │ 5. {status: \"success\"}   │                            │
     │\u003c─────────────────────────┤                            │
     │                          │                            │
```

---

## Seguridad

### API Keys
- Almacenadas en SQLite
- Nunca expuestas en logs
- Transmitidas solo via HTTPS en producción

### Command Execution
- Whitelist de comandos permitidos
- Timeout configurable
- Validación de paths

### CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"http://localhost:3000\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)
```

---

## Escalabilidad

### Horizontal Scaling
- Backend stateless (excepto WebSocket)
- Usar Redis para sesiones WebSocket
- Load balancer para múltiples instancias

### Vertical Scaling
- Async/await para I/O bound operations
- Connection pooling para DB
- Caching de configuración

### Performance
- WebSocket para reducir latencia
- Streaming de respuestas
- Lazy loading de tools

---

## Monitoreo

### Logs
```python
import logging

logger = logging.getLogger(__name__)
logger.info(\"Message processed\")
logger.error(\"Error in tool execution\", exc_info=True)
```

### Métricas
- Request count
- Response time
- Error rate
- WebSocket connections
- Tool execution time

### Health Checks
```bash
# Backend
curl http://localhost:8000/health

# Database
sqlite3 ~/.agent_data/conversations/agent.db \".tables\"
```

---

## Testing

### Unit Tests
```python
@pytest.mark.asyncio
async def test_agent_process_message():
    agent = AgentCore(mock_llm, AgentConfig())
    events = []
    async for event in agent.process_message(\"test\", \"conv_1\"):
        events.append(event)
    assert len(events) \u003e 0
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_websocket_chat():
    async with websockets.connect(\"ws://localhost:8000/ws/chat/test\") as ws:
        await ws.send(json.dumps({\"message\": \"test\"}))
        response = await ws.recv()
        assert json.loads(response)[\"type\"] == \"connected\"
```

---

## Deployment Architecture

### Development
```
┌──────────────┐
│   Localhost  │
│              │
│ Frontend:3000│
│ Backend:8000 │
│ SQLite       │
└──────────────┘
```

### Production
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────\u003e│   Backend   │────\u003e│  PostgreSQL │
│  (Reverse   │     │  (Uvicorn)  │     │             │
│   Proxy)    │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
      │
      │
┌─────────────┐
│  Frontend   │
│  (Static)   │
└─────────────┘
```

---

**Última actualización:** 2025-12-29
