# WebSocket - Guía de Uso

## 🌐 WebSocket para Streaming en Tiempo Real

El WebSocket permite recibir actualizaciones del agente en tiempo real mientras procesa mensajes y ejecuta tools.

## 📡 Endpoint

```
ws://localhost:8000/ws/chat/{conversation_id}
```

## 🔄 Flujo de Eventos

### 1. Conexión
El cliente se conecta al WebSocket y recibe confirmación:

```json
{
  "type": "connected",
  "conversation_id": "conv_123",
  "message": "Conexión establecida"
}
```

### 2. Enviar Mensaje
El cliente envía un mensaje:

```json
{
  "message": "Crea un archivo test.txt"
}
```

### 3. Recibir Eventos

El agente envía eventos en tiempo real:

#### Thinking Event
```json
{
  "type": "thinking",
  "iteration": 1
}
```

#### Tool Call Event
```json
{
  "type": "tool_call",
  "tool": "write_file",
  "arguments": {
    "path": "test.txt",
    "content": "Hello"
  },
  "tool_call_id": "call_1"
}
```

#### Tool Result Event
```json
{
  "type": "tool_result",
  "success": true,
  "result": {
    "path": "/path/to/test.txt",
    "size": 5
  }
}
```

#### Message Event
```json
{
  "type": "message",
  "content": "Archivo creado exitosamente"
}
```

#### Done Event
```json
{
  "type": "done",
  "iterations": 2
}
```

#### Error Event
```json
{
  "type": "error",
  "error": "Error message"
}
```

## 💻 Ejemplos de Uso

### JavaScript (Browser)

```javascript
// Conectar
const ws = new WebSocket('ws://localhost:8000/ws/chat/my_conversation');

// Escuchar eventos
ws.onopen = () => {
  console.log('Conectado');
  
  // Enviar mensaje
  ws.send(JSON.stringify({
    message: 'Hola, crea un archivo'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'connected':
      console.log('✅ Conexión establecida');
      break;
    
    case 'thinking':
      console.log(`🤔 Pensando... (iteración ${data.iteration})`);
      break;
    
    case 'tool_call':
      console.log(`🔧 Ejecutando: ${data.tool}`);
      console.log('   Args:', data.arguments);
      break;
    
    case 'tool_result':
      if (data.success) {
        console.log('✅ Tool ejecutado');
      } else {
        console.log('❌ Error:', data.error);
      }
      break;
    
    case 'message':
      console.log(`🤖 Agente: ${data.content}`);
      break;
    
    case 'done':
      console.log(`✓ Completado en ${data.iterations} iteraciones`);
      break;
    
    case 'error':
      console.error('❌ Error:', data.error);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Desconectado');
};
```

### Python (websockets)

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/chat/my_conversation"
    
    async with websockets.connect(uri) as websocket:
        # Esperar conexión
        event = await websocket.recv()
        data = json.loads(event)
        print(f"✅ {data['message']}")
        
        # Enviar mensaje
        await websocket.send(json.dumps({
            "message": "Lista archivos"
        }))
        
        # Recibir eventos
        while True:
            try:
                event = await websocket.recv()
                data = json.loads(event)
                
                if data['type'] == 'thinking':
                    print(f"🤔 Pensando...")
                
                elif data['type'] == 'tool_call':
                    print(f"🔧 {data['tool']}")
                
                elif data['type'] == 'message':
                    print(f"🤖 {data['content']}")
                
                elif data['type'] == 'done':
                    print("✓ Completado")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                break

asyncio.run(chat())
```

### React (Frontend)

```jsx
import { useEffect, useState } from 'react';

function Chat({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);
  
  useEffect(() => {
    const websocket = new WebSocket(
      `ws://localhost:8000/ws/chat/${conversationId}`
    );
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'message') {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.content
        }]);
      }
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, [conversationId]);
  
  const sendMessage = (text) => {
    ws.send(JSON.stringify({ message: text }));
    setMessages(prev => [...prev, {
      role: 'user',
      content: text
    }]);
  };
  
  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i}>{msg.content}</div>
      ))}
    </div>
  );
}
```

## 🔧 Características

- ✅ **Tiempo Real**: Eventos enviados instantáneamente
- ✅ **Múltiples Clientes**: Varios clientes pueden conectarse a la misma conversación
- ✅ **Reconexión**: Manejo automático de desconexiones
- ✅ **Eventos Tipados**: Cada evento tiene un tipo específico
- ✅ **Bidireccional**: Cliente y servidor pueden enviar mensajes

## 📊 Tipos de Eventos

| Tipo | Descripción | Cuándo se envía |
|------|-------------|-----------------|
| `connected` | Conexión establecida | Al conectar |
| `thinking` | Agente pensando | Inicio de iteración |
| `tool_call` | Se va a ejecutar tool | Antes de ejecutar |
| `tool_result` | Resultado de tool | Después de ejecutar |
| `message` | Respuesta del agente | Al finalizar |
| `error` | Error durante proceso | Si hay error |
| `done` | Proceso completado | Al terminar |

## 🚨 Manejo de Errores

```javascript
ws.onerror = (error) => {
  console.error('Error:', error);
  // Intentar reconectar
  setTimeout(() => {
    connectWebSocket();
  }, 3000);
};

ws.onclose = (event) => {
  if (event.wasClean) {
    console.log('Conexión cerrada limpiamente');
  } else {
    console.error('Conexión perdida');
    // Reconectar
  }
};
```

## 🔐 Seguridad (TODO)

- [ ] Autenticación con token
- [ ] Rate limiting por conexión
- [ ] Validación de mensajes
- [ ] Timeout de conexiones inactivas

## 📝 Notas

1. Cada conversación puede tener múltiples clientes conectados
2. Los eventos se envían a todos los clientes de la conversación
3. La conexión se cierra automáticamente si hay error
4. El agente mantiene el historial de la conversación

## 🧪 Testing

Ver `tests/test_websocket.py` para ejemplos de testing.

```bash
python3 tests/test_websocket.py
```
