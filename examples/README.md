# Agente Autónomo - Ejemplos de Uso

Ejemplos prácticos de cómo usar el agente autónomo.

## Instalación de Dependencias

```bash
cd /Users/lordzero1/IA_LoRdZeRo/auto
pip install -r requirements.txt
```

## Configurar API Key

```bash
# Opción 1: OpenAI
export OPENAI_API_KEY="sk-..."

# Opción 2: Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Opción 3: DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# Opción 4: Ollama (local, no requiere API key)
# Asegúrate de que Ollama esté corriendo
ollama serve
```

## Ejemplos Disponibles

### 1. Uso Básico (`basic_usage.py`)

Demuestra el uso completo del agente con múltiples tools.

```bash
python examples/basic_usage.py
```

**Qué hace:**
- Crea y lee archivos
- Ejecuta comandos shell
- Operaciones Git
- Tareas complejas con múltiples tools

### 2. Test de Tools (`test_tools.py`)

Prueba cada tool individualmente.

```bash
python examples/test_tools.py
```

**Qué hace:**
- Test de file operations
- Test de command execution
- Test de Git operations

## Uso Programático

### Ejemplo Mínimo

```python
import asyncio
from agent import AgentCore, AgentConfig, create_llm_provider
from tools import get_all_tools

async def main():
    # Crear agente
    llm = create_llm_provider("deepseek")
    agent = AgentCore(llm, AgentConfig())
    
    # Registrar tools
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    # Procesar mensaje
    async for event in agent.process_message(
        "Lista los archivos en el directorio actual",
        "conv_001"
    ):
        if event["type"] == "message":
            print(event["content"])

asyncio.run(main())
```

### Cambiar Proveedor de LLM

```python
# OpenAI
llm = create_llm_provider("openai", model="gpt-4")

# Anthropic
llm = create_llm_provider("anthropic", model="claude-3-5-sonnet-20241022")

# DeepSeek
llm = create_llm_provider("deepseek", model="deepseek-chat")

# Ollama (local)
llm = create_llm_provider("ollama", model="deepseek-coder:33b")
```

### Niveles de Autonomía

```python
# Autónomo total (ejecuta todo sin pedir)
config = AgentConfig(autonomy_level="full")

# Semi-autónomo (pide aprobación para acciones críticas)
config = AgentConfig(autonomy_level="semi")

# Supervisado (pide aprobación para todo)
config = AgentConfig(autonomy_level="supervised")
```

### Personalizar Tools que Requieren Aprobación

```python
config = AgentConfig(
    autonomy_level="semi",
    require_approval_for=[
        "delete_file",
        "execute_command",
        "git_commit"
    ]
)
```

## Ejemplos de Tareas

### Gestión de Archivos

```python
# Crear archivo
"Crea un archivo config.json con una configuración básica"

# Leer archivo
"Lee el contenido de README.md"

# Buscar archivos
"Busca todos los archivos Python en este proyecto"

# Eliminar archivo
"Elimina el archivo temporal.txt"
```

### Desarrollo

```python
# Crear script
"Crea un script Python que calcule números fibonacci"

# Ejecutar tests
"Ejecuta los tests con pytest"

# Git operations
"Haz commit de los cambios con mensaje 'feat: add new feature'"
```

### Comandos Shell

```python
# Ejecutar comando
"Ejecuta 'npm install' en el directorio frontend"

# Instalar paquete
"Instala el paquete requests con pip"

# Ver procesos
"Muestra los procesos de Python corriendo"
```

## Manejo de Eventos

El agente emite diferentes tipos de eventos:

```python
async for event in agent.process_message(message, conv_id):
    event_type = event["type"]
    
    if event_type == "thinking":
        # El agente está pensando
        print("Analizando...")
    
    elif event_type == "tool_call":
        # Va a ejecutar un tool
        tool = event["tool"]
        print(f"Ejecutando: {tool}")
    
    elif event_type == "tool_result":
        # Resultado de tool
        if event["success"]:
            print(f"✓ {event['result']}")
        else:
            print(f"✗ {event['error']}")
    
    elif event_type == "approval_required":
        # Requiere aprobación
        print("⚠️ Requiere aprobación")
        # Aquí pedirías confirmación al usuario
    
    elif event_type == "message":
        # Respuesta final
        print(f"Agente: {event['content']}")
    
    elif event_type == "done":
        # Completado
        print("Listo!")
```

## Troubleshooting

### Error: "No API key configured"

Asegúrate de configurar la API key:
```bash
export DEEPSEEK_API_KEY="tu-api-key"
```

### Error: "Tool not found"

Verifica que hayas registrado los tools:
```python
for tool in get_all_tools():
    agent.register_tool(tool)
```

### Error: "Command blocked"

Algunos comandos están bloqueados por seguridad. Revisa `command_tools.py` para ver la lista.

## Próximos Pasos

- Ver [Documentación Completa](../Docs/README.md)
- Crear [Tools Personalizados](../Docs/development/custom-tools.md)
- Configurar [Backend API](../Docs/api/backend-api.md)
