# Backend API Reference

Documentación de la API REST y WebSocket del backend.

## Base URL

- **Desarrollo**: `http://localhost:8000`
- **Producción**: `https://api.tudominio.com`

## Autenticación

Todas las requests requieren autenticación vía JWT token.

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Usar Token

```http
GET /api/conversations
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Endpoints

### Chat

#### Enviar Mensaje

```http
POST /api/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "conversation_id": "conv_123",
  "message": "Lista las instancias EC2",
  "stream": true
}
```

**Response (streaming):**
```
data: {"type": "thinking", "content": "Analizando request..."}

data: {"type": "tool_call", "tool": "list_ec2_instances", "params": {}}

data: {"type": "tool_result", "result": [...]}

data: {"type": "message", "content": "Encontré 5 instancias..."}

data: {"type": "done"}
```

### Conversaciones

#### Listar Conversaciones

```http
GET /api/conversations
Authorization: Bearer {token}
```

**Response:**
```json
{
  "conversations": [
    {
      "id": "conv_123",
      "title": "Gestión de AWS",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:45:00Z",
      "message_count": 12
    }
  ]
}
```

#### Crear Conversación

```http
POST /api/conversations
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Nueva conversación"
}
```

#### Obtener Conversación

```http
GET /api/conversations/{conversation_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "conv_123",
  "title": "Gestión de AWS",
  "messages": [
    {
      "role": "user",
      "content": "Lista las instancias",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Encontré 5 instancias...",
      "timestamp": "2024-01-15T10:30:05Z",
      "tool_calls": [...]
    }
  ]
}
```

#### Eliminar Conversación

```http
DELETE /api/conversations/{conversation_id}
Authorization: Bearer {token}
```

### Configuración

#### Obtener Configuración

```http
GET /api/config
Authorization: Bearer {token}
```

**Response:**
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4"
  },
  "agent": {
    "autonomy_level": "semi"
  },
  "cloud_providers": {
    "aws": {"enabled": true},
    "azure": {"enabled": true},
    "gcp": {"enabled": false}
  }
}
```

#### Actualizar Configuración

```http
PUT /api/config
Authorization: Bearer {token}
Content-Type: application/json

{
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet"
  }
}
```

### Métricas

#### Obtener Métricas

```http
GET /api/metrics
Authorization: Bearer {token}
```

**Response:**
```json
{
  "alerts": {
    "critical": 2,
    "warning": 5,
    "ok": 120
  },
  "infrastructure": {
    "aws_instances": 15,
    "azure_vms": 8,
    "gcp_instances": 0
  },
  "agent_stats": {
    "total_messages": 1250,
    "tools_executed": 3420,
    "uptime_seconds": 86400
  }
}
```

### Tools

#### Listar Tools Disponibles

```http
GET /api/tools
Authorization: Bearer {token}
```

**Response:**
```json
{
  "tools": [
    {
      "name": "list_ec2_instances",
      "description": "Lista instancias EC2",
      "category": "aws",
      "parameters": {...}
    }
  ]
}
```

#### Ejecutar Tool Directamente

```http
POST /api/tools/execute
Authorization: Bearer {token}
Content-Type: application/json

{
  "tool": "list_ec2_instances",
  "parameters": {
    "region": "us-east-1"
  }
}
```

### APIs Aprendidas

#### Listar APIs

```http
GET /api/learned-apis
Authorization: Bearer {token}
```

**Response:**
```json
{
  "apis": [
    {
      "id": "api_jira",
      "name": "Jira API",
      "endpoints": 47,
      "learned_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

#### Aprender API

```http
POST /api/learned-apis
Authorization: Bearer {token}
Content-Type: application/json

{
  "type": "openapi",
  "source": "https://api.example.com/swagger.json"
}
```

## WebSocket

### Conexión

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'eyJhbGciOiJIUzI1NiIs...'
  }));
};
```

### Mensajes

#### Enviar Mensaje

```javascript
ws.send(JSON.stringify({
  type: 'chat',
  conversation_id: 'conv_123',
  message: 'Lista las instancias EC2'
}));
```

#### Recibir Respuestas

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'thinking':
      console.log('Agente pensando...');
      break;
    case 'tool_call':
      console.log('Ejecutando:', data.tool);
      break;
    case 'message':
      console.log('Respuesta:', data.content);
      break;
  }
};
```

## Códigos de Error

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

**Formato de Error:**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "El parámetro 'message' es requerido",
    "details": {}
  }
}
```

## Rate Limiting

- **Límite**: 60 requests por minuto por usuario
- **Headers de respuesta**:
  - `X-RateLimit-Limit`: 60
  - `X-RateLimit-Remaining`: 45
  - `X-RateLimit-Reset`: 1642345678

## Webhooks

Configura webhooks para recibir notificaciones de eventos.

### Configurar Webhook

```http
POST /api/webhooks
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://tu-servidor.com/webhook",
  "events": ["alert.critical", "tool.executed"],
  "secret": "tu-secreto"
}
```

### Eventos Disponibles

- `alert.critical` - Alerta crítica detectada
- `alert.warning` - Alerta de advertencia
- `tool.executed` - Tool ejecutado
- `conversation.created` - Nueva conversación
- `api.learned` - Nueva API aprendida

## SDK (Próximamente)

```python
from agent_client import AgentClient

client = AgentClient(api_key="tu-api-key")

# Enviar mensaje
response = client.chat.send(
    conversation_id="conv_123",
    message="Lista las instancias EC2"
)

# Ejecutar tool
result = client.tools.execute(
    "list_ec2_instances",
    region="us-east-1"
)
```

## Próximos Pasos

- [Referencia de Tools](tools-reference.md)
- [Guía de Desarrollo](../development/contributing.md)
