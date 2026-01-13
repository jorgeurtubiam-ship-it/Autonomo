# 📡 API Reference Completa

## Tabla de Contenidos

1. [REST API](#rest-api)
2. [WebSocket API](#websocket-api)
3. [Models](#models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Authentication](#authentication)

---

## REST API

### Base URL

```
Development: http://localhost:8000
Production: https://api.tudominio.com
```

### Headers

```http
Content-Type: application/json
Accept: application/json
```

---

## Endpoints

### Health Check

Verifica el estado del servidor.

```http
GET /health
```

**Response 200 OK:**
```json
{
  \"status\": \"healthy\",
  \"service\": \"agent-api\",
  \"version\": \"1.0.0\",
  \"uptime_seconds\": 123.45
}
```

**Ejemplo:**
```bash
curl http://localhost:8000/health
```

---

### Configuration

#### Get Configuration

Obtiene la configuración actual del agente.

```http
GET /api/config/
```

**Response 200 OK:**
```json
{
  \"llm_provider\": \"deepseek\",
  \"model\": \"deepseek-chat\",
  \"autonomy_level\": \"semi\",
  \"temperature\": 0.7,
  \"max_tokens\": 4000,
  \"tools_count\": 15
}
```

**Ejemplo:**
```bash
curl http://localhost:8000/api/config/
```

#### Update Configuration

Actualiza la configuración del agente.

```http
PUT /api/config/
Content-Type: application/json
```

**Request Body:**
```json
{
  \"llm_provider\": \"deepseek\",
  \"model\": \"deepseek-chat\",
  \"api_keys\": {
    \"deepseek\": \"sk-...\"
  },
  \"temperature\": 0.7,
  \"max_tokens\": 4000
}
```

**Response 200 OK:**
```json
{
  \"status\": \"success\",
  \"message\": \"Configuración actualizada\",
  \"config\": {
    \"llm_provider\": \"deepseek\",
    \"model\": \"deepseek-chat\",
    \"deepseek_api_key\": \"***\"
  }
}
```

**Ejemplo:**
```bash
curl -X PUT http://localhost:8000/api/config/ \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"llm_provider\": \"deepseek\",
    \"model\": \"deepseek-chat\",
    \"api_keys\": {
      \"deepseek\": \"sk-bc52dbe1e60747f2877e85a88d4309a8\"
    }
  }'
```

---

### Conversations

#### List Conversations

Obtiene la lista de todas las conversaciones.

```http
GET /api/conversations/
```

**Query Parameters:**
- `limit` (optional): Número máximo de conversaciones (default: 50)
- `offset` (optional): Offset para paginación (default: 0)

**Response 200 OK:**
```json
[
  {
    \"id\": \"conv_1766778113478\",
    \"title\": \"hola como estas?\",
    \"created_at\": \"2025-12-26T16:42:10Z\",
    \"updated_at\": \"2025-12-26T16:42:15Z\",
    \"message_count\": 4
  },
  {
    \"id\": \"conv_1766778256812\",
    \"title\": \"me puedes mostrar los procesos...\",
    \"created_at\": \"2025-12-26T16:44:37Z\",
    \"updated_at\": \"2025-12-26T16:44:42Z\",
    \"message_count\": 2
  }
]
```

**Ejemplo:**
```bash
curl http://localhost:8000/api/conversations/
```

#### Get Conversation

Obtiene una conversación específica.

```http
GET /api/conversations/{conversation_id}
```

**Path Parameters:**
- `conversation_id`: ID de la conversación

**Response 200 OK:**
```json
{
  \"id\": \"conv_1766778113478\",
  \"title\": \"hola como estas?\",
  \"created_at\": \"2025-12-26T16:42:10Z\",
  \"updated_at\": \"2025-12-26T16:42:15Z\",
  \"message_count\": 4
}
```

**Response 404 Not Found:**
```json
{
  \"detail\": \"Conversación conv_123 no encontrada\"
}
```

#### Delete Conversation

Elimina una conversación y todos sus mensajes.

```http
DELETE /api/conversations/{conversation_id}
```

**Path Parameters:**
- `conversation_id`: ID de la conversación

**Response 200 OK:**
```json
{
  \"status\": \"success\",
  \"message\": \"Conversación conv_123 eliminada\",
  \"conversation_id\": \"conv_123\"
}
```

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8000/api/conversations/conv_123
```

#### Update Conversation Title

Actualiza el título de una conversación.

```http
POST /api/conversations/{conversation_id}/title
Content-Type: application/json
```

**Request Body:**
```json
{
  \"title\": \"Nuevo título\"
}
```

**Response 200 OK:**
```json
{
  \"status\": \"success\",
  \"conversation_id\": \"conv_123\",
  \"title\": \"Nuevo título\"
}
```

---

### Chat

#### Get Conversation History

Obtiene el historial completo de una conversación.

```http
GET /api/chat/{conversation_id}/history
```

**Path Parameters:**
- `conversation_id`: ID de la conversación

**Response 200 OK:**
```json
{
  \"conversation_id\": \"conv_123\",
  \"messages\": [
    {
      \"id\": 1,
      \"role\": \"user\",
      \"content\": \"Hola, ¿cómo estás?\",
      \"tool_calls\": null,
      \"created_at\": \"2025-12-26T16:42:10Z\"
    },
    {
      \"id\": 2,
      \"role\": \"assistant\",
      \"content\": \"¡Hola! Estoy bien, gracias. ¿En qué puedo ayudarte?\",
      \"tool_calls\": null,
      \"created_at\": \"2025-12-26T16:42:11Z\"
    },
    {
      \"id\": 3,
      \"role\": \"user\",
      \"content\": \"Crea un archivo test.txt\",
      \"tool_calls\": null,
      \"created_at\": \"2025-12-26T16:42:15Z\"
    },
    {
      \"id\": 4,
      \"role\": \"assistant\",
      \"content\": \"He creado el archivo test.txt correctamente.\",
      \"tool_calls\": [
        {
          \"name\": \"write_file\",
          \"arguments\": {
            \"path\": \"test.txt\",
            \"content\": \"Contenido del archivo\"
          }
        }
      ],
      \"created_at\": \"2025-12-26T16:42:16Z\"
    }
  ]
}
```

**Response 404 Not Found:**
```json
{
  \"detail\": \"Conversación conv_123 no encontrada\"
}
```

#### Send Message (REST)

Envía un mensaje y obtiene la respuesta completa (sin streaming).

```http
POST /api/chat/
Content-Type: application/json
```

**Request Body:**
```json
{
  \"message\": \"Hola, ¿cómo estás?\",
  \"conversation_id\": \"conv_123\"
}
```

**Response 200 OK:**
```json
{
  \"message\": \"¡Hola! Estoy bien, gracias. ¿En qué puedo ayudarte?\",
  \"conversation_id\": \"conv_123\",
  \"tool_calls\": []
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/chat/ \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"message\": \"Hola\",
    \"conversation_id\": \"conv_123\"
  }'
```

---

## WebSocket API

### Connect

Establece una conexión WebSocket para chat en tiempo real.

```
ws://localhost:8000/ws/chat/{conversation_id}
```

**Path Parameters:**
- `conversation_id`: ID de la conversación

**Ejemplo JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/conv_123');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Send Message

```javascript
ws.send(JSON.stringify({
  message: \"Hola, ¿cómo estás?\"
}));
```

### Message Types

#### Connected

Enviado por el servidor al conectar.

```json
{
  \"type\": \"connected\"
}
```

#### Thinking

Indica que el agente está procesando.

```json
{
  \"type\": \"thinking\"
}
```

#### Tool Call

Indica que se ha generado una llamada a herramienta.

```json
{
  "type": "tool_call",
  "name": "execute_command",
  "id": "call_abc123",
  "arguments": {
    "command": "ls -la"
  }
}
```

#### Tool Result

Resultado de la ejecución de una herramienta.

```json
{
  "type": "tool_result",
  "tool": "execute_command",
  "id": "call_abc123",
  "result": {
    "success": true,
    "result": "total 0...",
    "error": null
  }
}
```

#### Message Chunk

Fragmento de la respuesta del agente (streaming).

```json
{
  \"type\": \"message_chunk\",
  \"content\": \"Hola\"
}
```

#### Message

Mensaje completo del agente.

```json
{
  \"type\": \"message\",
  \"content\": \"¡Hola! ¿En qué puedo ayudarte?\"
}
```

#### Done

Indica que el procesamiento ha terminado.

```json
{
  \"type\": \"done\"
}
```

#### Error

Indica que ocurrió un error.

```json
{
  \"type\": \"error\",
  \"error\": \"Error message\",
  \"message\": \"Detailed error description\"
}
```

---

## Models

### ConfigUpdate

```python
class ConfigUpdate(BaseModel):
    llm_provider: Optional[str] = None
    model: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
```

### ConfigResponse

```python
class ConfigResponse(BaseModel):
    llm_provider: str
    model: str
    autonomy_level: str
    temperature: float
    max_tokens: int
    tools_count: int
```

### ChatRequest

```python
class ChatRequest(BaseModel):
    message: str
    conversation_id: str
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    tool_calls: List[Dict[str, Any]] = []
```

### Conversation

```python
class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
```

### Message

```python
class Message(BaseModel):
    id: int
    conversation_id: str
    role: str  # \"user\" | \"assistant\"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Solicitud exitosa
- `400 Bad Request` - Request inválido
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor

### Error Response Format

```json
{
  \"detail\": \"Error message\"
}
```

### Common Errors

#### Invalid Configuration

```json
{
  \"detail\": \"Invalid LLM provider: invalid_provider\"
}
```

#### Conversation Not Found

```json
{
  \"detail\": \"Conversación conv_123 no encontrada\"
}
```

#### Missing API Key

```json
{
  \"detail\": \"API key not configured for provider: deepseek\"
}
```

---

## Rate Limiting

Actualmente no hay rate limiting implementado.

**Recomendaciones para producción:**
- Implementar rate limiting por IP
- Límite: 100 requests/minuto
- Límite WebSocket: 10 conexiones simultáneas por IP

---

## Authentication

Actualmente no hay autenticación implementada.

**Recomendaciones para producción:**
- Implementar JWT tokens
- OAuth 2.0 para integración con terceros
- API keys para acceso programático

---

## Ejemplos Completos

### Python

```python
import requests
import json

# Base URL
BASE_URL = \"http://localhost:8000\"

# Get configuration
response = requests.get(f\"{BASE_URL}/api/config/\")
config = response.json()
print(\"Config:\", config)

# Update configuration
response = requests.put(
    f\"{BASE_URL}/api/config/\",
    json={
        \"llm_provider\": \"deepseek\",
        \"model\": \"deepseek-chat\"
    }
)
print(\"Update:\", response.json())

# List conversations
response = requests.get(f\"{BASE_URL}/api/conversations/\")
conversations = response.json()
print(\"Conversations:\", conversations)

# Send message
response = requests.post(
    f\"{BASE_URL}/api/chat/\",
    json={
        \"message\": \"Hola\",
        \"conversation_id\": \"conv_123\"
    }
)
print(\"Response:\", response.json())
```

### JavaScript

```javascript
// Base URL
const BASE_URL = 'http://localhost:8000';

// Get configuration
fetch(`${BASE_URL}/api/config/`)
  .then(res => res.json())
  .then(config => console.log('Config:', config));

// Update configuration
fetch(`${BASE_URL}/api/config/`, {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    llm_provider: 'deepseek',
    model: 'deepseek-chat'
  })
})
  .then(res => res.json())
  .then(data => console.log('Update:', data));

// WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/chat/conv_123`);

ws.onopen = () => {
  ws.send(JSON.stringify({message: 'Hola'}));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message:', data);
};
```

### cURL

```bash
# Get config
curl http://localhost:8000/api/config/

# Update config
curl -X PUT http://localhost:8000/api/config/ \\
  -H \"Content-Type: application/json\" \\
  -d '{\"llm_provider\": \"deepseek\", \"model\": \"deepseek-chat\"}'

# List conversations
curl http://localhost:8000/api/conversations/

# Get history
curl http://localhost:8000/api/chat/conv_123/history

# Delete conversation
curl -X DELETE http://localhost:8000/api/conversations/conv_123
```

---

**Última actualización:** 2025-12-29
