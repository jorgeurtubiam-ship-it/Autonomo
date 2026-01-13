# Core del Agente - Documentación Técnica

Documentación técnica de los componentes core del agente.

## Componentes

### 1. LLM Provider (`llm_provider.py`)

Abstracción para múltiples proveedores de LLM.

#### Proveedores Soportados

**OpenAI**
- Modelos: GPT-4, GPT-4o, GPT-3.5-turbo
- API Key: `OPENAI_API_KEY`
- Características: Tool calling, streaming

**Anthropic**
- Modelos: Claude 3.5 Sonnet, Claude 3 Opus
- API Key: `ANTHROPIC_API_KEY`
- Características: Tool calling, streaming

**DeepSeek**
- Modelos: deepseek-chat, deepseek-coder
- API Key: `DEEPSEEK_API_KEY`
- Base URL: `https://api.deepseek.com`
- Características: API compatible con OpenAI, tool calling, streaming

**Ollama**
- Modelos: Cualquier modelo local (deepseek-coder, llama3, etc.)
- Sin API key (local)
- Base URL: `http://localhost:11434`
- Características: Gratis, privado, sin límites

#### Uso

```python
from agent import create_llm_provider

# OpenAI
llm = create_llm_provider("openai", model="gpt-4", api_key="sk-...")

# Anthropic
llm = create_llm_provider("anthropic", model="claude-3-5-sonnet-20241022")

# DeepSeek
llm = create_llm_provider("deepseek", model="deepseek-chat")

# Ollama
llm = create_llm_provider("ollama", model="deepseek-coder:33b")

# Usar el LLM
from agent import Message

messages = [
    Message(role="system", content="Eres un asistente útil"),
    Message(role="user", content="Hola")
]

response = await llm.chat(messages)
print(response.content)
```

#### Streaming

```python
async for chunk in llm.chat_stream(messages):
    print(chunk, end="", flush=True)
```

### 2. System Prompts (`prompts.py`)

Define el comportamiento del agente.

#### System Prompt Principal

Incluye:
- Identidad del agente
- Capacidades (tools disponibles)
- Ciclo Plan & Act
- Reglas de seguridad
- Formato de respuestas
- Ejemplos de uso

#### Obtener System Prompt

```python
from agent import get_system_prompt

# Con instrucciones de tools
prompt = get_system_prompt(include_tool_instructions=True)

# Sin instrucciones de tools
prompt = get_system_prompt(include_tool_instructions=False)
```

### 3. Context Manager (`context.py`)

Gestiona conversaciones y memoria.

#### Crear Conversación

```python
from agent import ContextManager

context = ContextManager()

# Crear nueva conversación
conv = context.create_conversation("conv_123")

# Agregar mensajes
context.add_message("user", "Hola", "conv_123")
context.add_message("assistant", "¡Hola! ¿En qué puedo ayudarte?", "conv_123")

# Obtener mensajes
messages = context.get_messages("conv_123")
```

#### Export/Import

```python
# Exportar conversación
json_data = context.export_conversation("conv_123")

# Importar conversación
context.import_conversation(json_data)
```

### 4. Agent Core (`core.py`)

Motor principal con ciclo Plan & Act.

#### Configuración

```python
from agent import AgentCore, AgentConfig, create_llm_provider

# Configurar agente
config = AgentConfig(
    autonomy_level="semi",  # full, semi, supervised
    max_iterations=10,
    require_approval_for=["delete_file", "terminate_instance"]
)

# Crear LLM
llm = create_llm_provider("openai", model="gpt-4")

# Crear agente
agent = AgentCore(llm, config)
```

#### Registrar Tools

```python
# Registrar un tool
agent.register_tool(my_tool)

# Ver tools registrados
tools = agent.tool_registry.list_tools()
```

#### Procesar Mensajes

```python
# Procesar mensaje del usuario
async for event in agent.process_message(
    user_message="Lista los archivos",
    conversation_id="conv_123",
    stream=True
):
    if event["type"] == "thinking":
        print("Pensando...")
    
    elif event["type"] == "tool_call":
        print(f"Ejecutando: {event['tool']}")
    
    elif event["type"] == "tool_result":
        print(f"Resultado: {event['result']}")
    
    elif event["type"] == "message":
        print(f"Respuesta: {event['content']}")
    
    elif event["type"] == "done":
        print("Completado")
```

#### Eventos

El agente emite los siguientes eventos:

- `thinking`: El agente está analizando
- `tool_call`: Va a ejecutar un tool
- `tool_result`: Resultado de un tool
- `approval_required`: Requiere aprobación del usuario
- `message`: Mensaje final del agente
- `error`: Error en el procesamiento
- `done`: Procesamiento completado

## Ciclo Plan & Act

```
1. Usuario envía mensaje
   ↓
2. Agente analiza (PLAN)
   ↓
3. LLM decide qué tools usar
   ↓
4. Ejecuta tools (ACT)
   ↓
5. LLM procesa resultados
   ↓
6. ¿Necesita más tools?
   Sí → Volver a paso 3
   No → Responder al usuario
```

## Niveles de Autonomía

### Full (Autónomo Total)
- Ejecuta todos los tools automáticamente
- Sin aprobación del usuario
- Rápido pero potencialmente peligroso

### Semi (Recomendado)
- Ejecuta tools seguros automáticamente
- Pide aprobación para acciones críticas
- Balance entre velocidad y seguridad

### Supervised (Supervisado)
- Pide aprobación para TODOS los tools
- Máxima seguridad
- Más lento

## Ejemplo Completo

```python
import asyncio
from agent import (
    AgentCore,
    AgentConfig,
    create_llm_provider
)

async def main():
    # Configurar
    config = AgentConfig(autonomy_level="semi")
    llm = create_llm_provider("deepseek", model="deepseek-chat")
    agent = AgentCore(llm, config)
    
    # Registrar tools (ejemplo)
    # agent.register_tool(list_files_tool)
    # agent.register_tool(read_file_tool)
    
    # Procesar mensaje
    async for event in agent.process_message(
        user_message="¿Qué archivos hay en el directorio actual?",
        conversation_id="conv_001"
    ):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

```python
import pytest
from agent import create_llm_provider, Message

@pytest.mark.asyncio
async def test_llm_provider():
    llm = create_llm_provider("openai", model="gpt-3.5-turbo")
    
    messages = [
        Message(role="user", content="Di hola")
    ]
    
    response = await llm.chat(messages)
    
    assert response.content
    assert "hola" in response.content.lower()
```

## Próximos Pasos

- Implementar tools fundamentales
- Agregar persistencia (database)
- Sistema de aprobación interactivo
- Métricas y logging
