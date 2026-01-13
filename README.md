# Agente Autónomo de Propósito General

Agente autónomo basado en la arquitectura de **Cline**, capaz de programar, gestionar infraestructura, monitorear sistemas y aprender nuevas APIs dinámicamente.

## 🎯 Características

- 🧠 **Multi-LLM**: OpenAI, Anthropic, DeepSeek, Ollama
- 📁 **File Operations**: Leer, escribir, buscar archivos
- ⚡ **Command Execution**: Ejecutar comandos shell y scripts
- 🔧 **Git Integration**: Status, diff, commit, log
- ☁️ **Multi-Cloud**: AWS, Azure, GCP (próximamente)
- 🤖 **Aprendizaje Dinámico**: Aprende APIs desde documentación
- 🔒 **Seguridad**: Comandos bloqueados, timeouts, validación

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key

```bash
# Opción 1: DeepSeek (recomendado)
export DEEPSEEK_API_KEY="sk-..."

# Opción 2: OpenAI
export OPENAI_API_KEY="sk-..."

# Opción 3: Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Opción 4: Ollama (local, gratis)
ollama serve
```

### 3. Ejecutar Ejemplo

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
    
    # Usar el agente
    async for event in agent.process_message(
        "Crea un archivo hello.txt con 'Hola Mundo'",
        "conv_001"
    ):
        if event["type"] == "message":
            print(event["content"])

asyncio.run(main())
```

O ejecuta el ejemplo completo:

```bash
python examples/basic_usage.py
```

## 📚 Documentación

Para una guía detallada, consulta nuestro **[Índice de Documentación](Docs/README.md)**.

- [Guía de Inicio Rápido](Docs/QUICKSTART.md) ⭐
- [Arquitectura del Sistema](Docs/ARCHITECTURE.md)
- [Referencia de API](Docs/API_REFERENCE.md)
- [Interfaz de Usuario](Docs/USER_INTERFACE.md)
- [Crear Tools Personalizados](Docs/development/custom-tools.md)

## 🛠️ Tools Disponibles

### File Operations
- `read_file` - Leer archivos
- `write_file` - Crear/escribir archivos
- `list_directory` - Listar directorios
- `search_files` - Buscar archivos
- `delete_file` - Eliminar archivos
- `get_file_info` - Info de archivos

### Command Execution
- `execute_command` - Ejecutar comandos shell
- `run_script` - Ejecutar scripts (Python, Bash, Node, etc.)
- `install_package` - Instalar paquetes (pip, npm, etc.)

### Git Operations
- `git_status` - Estado del repositorio
- `git_diff` - Ver cambios
- `git_commit` - Hacer commits
- `git_log` - Historial de commits

## 🏗️ Arquitectura

```
Model (LLM) + Tools + Instructions = Agente Autónomo
         ↓
   Ciclo Plan & Act
         ↓
  1. Analizar tarea
  2. Planificar acciones
  3. Ejecutar tools
  4. Verificar resultados
  5. Responder al usuario
```

### Componentes

- **Agent Core** (`backend/agent/core.py`) - Motor principal
- **LLM Provider** (`backend/agent/llm_provider.py`) - Abstracción multi-LLM
- **Context Manager** (`backend/agent/context.py`) - Memoria y conversaciones
- **Tools** (`backend/tools/`) - Herramientas extensibles

## 💡 Ejemplos de Uso

### Gestión de Archivos

```python
"Crea un archivo config.json con configuración básica"
"Lee el contenido de README.md"
"Busca todos los archivos Python en este proyecto"
```

### Desarrollo

```python
"Crea un script Python que calcule fibonacci"
"Haz commit de los cambios con mensaje 'feat: add feature'"
"Ejecuta los tests con pytest"
```

### Comandos Shell

```python
"Ejecuta 'npm install' en el directorio frontend"
"Instala el paquete requests con pip"
"Lista los procesos de Python corriendo"
```

## 🔧 Configuración

### Niveles de Autonomía

```python
# Autónomo total
config = AgentConfig(autonomy_level="full")

# Semi-autónomo (recomendado)
config = AgentConfig(autonomy_level="semi")

# Supervisado
config = AgentConfig(autonomy_level="supervised")
```

### Cambiar LLM

```python
# DeepSeek
llm = create_llm_provider("deepseek", model="deepseek-chat")

# OpenAI
llm = create_llm_provider("openai", model="gpt-4")

# Anthropic
llm = create_llm_provider("anthropic", model="claude-3-5-sonnet-20241022")

# Ollama (local)
llm = create_llm_provider("ollama", model="deepseek-coder:33b")
```

## 📁 Estructura del Proyecto

```
auto/
├── backend/
│   ├── agent/          # Core del agente
│   │   ├── core.py     # Motor principal
│   │   ├── llm_provider.py  # Multi-LLM
│   │   ├── context.py  # Memoria
│   │   └── prompts.py  # System prompts
│   └── tools/          # Tools
│       ├── file_tools.py
│       ├── command_tools.py
│       └── git_tools.py
├── examples/           # Ejemplos de uso
├── Docs/              # Documentación completa
└── requirements.txt   # Dependencias
```

## 🧪 Testing

```bash
# Test de tools individuales
python examples/test_tools.py

# Tests unitarios (próximamente)
pytest tests/
```

## 🚧 Roadmap

- [x] Core del agente con ciclo Plan & Act
- [x] Multi-LLM (OpenAI, Anthropic, DeepSeek, Ollama)
- [x] Tools fundamentales (archivos, comandos, Git)
- [x] Backend API (FastAPI + WebSocket)
- [x] Frontend web (Live Terminal, Glassmorphism)
- [x] Resiliencia de Tools y Fallback Parsing
- [ ] Tools de Cloud avanzados (AWS native, Azure, GCP)
- [ ] Aprendizaje dinámico de APIs
- [ ] Sistema RAG para documentación

## 📄 Licencia

MIT License

## 🤝 Contribuir

Ver [Guía de Contribución](Docs/development/contributing.md)

## 💬 Soporte

- Documentación: [Docs/](Docs/)
- Issues: GitHub Issues
- Ejemplos: [examples/](examples/)
