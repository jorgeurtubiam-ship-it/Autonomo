# Backend API - Plan de Implementación

## Objetivo
Crear una API REST con FastAPI que exponga el agente autónomo, incluyendo WebSocket para streaming en tiempo real.

## Componentes a Implementar

### 1. Estructura Base
```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # App FastAPI principal
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py          # Endpoints de chat
│   │   ├── conversations.py # Gestión de conversaciones
│   │   └── health.py        # Health checks
│   ├── websocket/
│   │   ├── __init__.py
│   │   └── chat_ws.py       # WebSocket para streaming
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Modelos de request
│   │   └── responses.py     # Modelos de response
│   └── dependencies.py      # Dependencias compartidas
```

### 2. Endpoints REST

#### Chat
- `POST /api/chat` - Enviar mensaje al agente
- `GET /api/chat/{conversation_id}/history` - Obtener historial

#### Conversaciones
- `GET /api/conversations` - Listar conversaciones
- `POST /api/conversations` - Crear conversación
- `DELETE /api/conversations/{id}` - Eliminar conversación

#### Configuración
- `GET /api/config` - Obtener configuración
- `PUT /api/config` - Actualizar configuración

#### Health
- `GET /health` - Health check
- `GET /api/tools` - Listar tools disponibles

### 3. WebSocket
- `WS /ws/chat/{conversation_id}` - Streaming de respuestas

### 4. Modelos de Datos

#### Request Models
```python
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str]
    stream: bool = False
    
class ConfigUpdate(BaseModel):
    llm_provider: Optional[str]
    model: Optional[str]
    autonomy_level: Optional[str]
```

#### Response Models
```python
class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    tool_calls: Optional[List[Dict]]
    
class ConversationInfo(BaseModel):
    id: str
    created_at: datetime
    message_count: int
```

### 5. Características

- ✅ CORS habilitado
- ✅ Validación con Pydantic
- ✅ Manejo de errores
- ✅ Logging
- ✅ Rate limiting (opcional)
- ✅ Documentación automática (Swagger)

## Fases de Implementación

### Fase 1: Base ✅
1. Crear estructura de carpetas
2. Configurar FastAPI app
3. Health check endpoint

### Fase 2: Chat REST
1. Endpoint POST /api/chat
2. Modelos de request/response
3. Integración con AgentCore
4. Tests

### Fase 3: WebSocket
1. Endpoint WebSocket
2. Streaming de eventos
3. Manejo de conexiones
4. Tests

### Fase 4: Conversaciones
1. Endpoints CRUD
2. Persistencia (opcional)
3. Tests

### Fase 5: Configuración
1. Endpoints de config
2. Validación
3. Tests

## Tests a Implementar

1. **test_api_health.py** - Health checks
2. **test_api_chat.py** - Endpoints de chat
3. **test_api_websocket.py** - WebSocket
4. **test_api_integration.py** - Tests de integración

## Documentación

- API Reference en Swagger (automático)
- Ejemplos de uso con curl
- Ejemplos con Python requests
- Ejemplos con JavaScript fetch
