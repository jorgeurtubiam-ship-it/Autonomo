"""
Ejemplo de uso completo del Agente Autónomo
Demuestra cómo usar el agente con los tools implementados
"""

import asyncio
from agent import (
    AgentCore,
    AgentConfig,
    create_llm_provider
)
from tools import get_all_tools


async def main():
    """Ejemplo principal"""
    
    print("🤖 Inicializando Agente Autónomo...\n")
    
    # 1. Configurar el agente
    config = AgentConfig(
        autonomy_level="semi",  # Pide aprobación para acciones críticas
        max_iterations=10
    )
    
    # 2. Crear proveedor de LLM
    # Puedes usar: "openai", "anthropic", "deepseek", "ollama"
    llm = create_llm_provider(
        "deepseek",  # Cambia según tu preferencia
        model="deepseek-chat"
    )
    
    # 3. Crear agente
    agent = AgentCore(llm, config)
    
    # 4. Registrar todos los tools
    print("📦 Registrando tools...")
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    tools_list = agent.tool_registry.list_tools()
    print(f"✅ {len(tools_list)} tools registrados: {', '.join(tools_list)}\n")
    
    # 5. Ejemplos de uso
    conversation_id = "demo_001"
    
    # Ejemplo 1: Gestión de archivos
    print("=" * 60)
    print("EJEMPLO 1: Gestión de Archivos")
    print("=" * 60)
    
    await process_message(
        agent,
        "Crea un archivo llamado 'test.txt' con el contenido 'Hola desde el agente autónomo'",
        conversation_id
    )
    
    await process_message(
        agent,
        "Lee el archivo test.txt",
        conversation_id
    )
    
    # Ejemplo 2: Comandos shell
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Ejecución de Comandos")
    print("=" * 60)
    
    await process_message(
        agent,
        "Lista los archivos en el directorio actual",
        conversation_id
    )
    
    # Ejemplo 3: Git
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Operaciones Git")
    print("=" * 60)
    
    await process_message(
        agent,
        "Muestra el estado de Git en este repositorio",
        conversation_id
    )
    
    # Ejemplo 4: Tarea compleja
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Tarea Compleja (múltiples tools)")
    print("=" * 60)
    
    await process_message(
        agent,
        "Crea un script Python llamado 'hello.py' que imprima 'Hello World', luego ejecútalo",
        conversation_id
    )
    
    print("\n✅ Ejemplos completados!")


async def process_message(agent, message, conversation_id):
    """
    Procesa un mensaje y muestra los eventos
    
    Args:
        agent: Instancia del agente
        message: Mensaje del usuario
        conversation_id: ID de la conversación
    """
    print(f"\n👤 Usuario: {message}\n")
    
    async for event in agent.process_message(message, conversation_id):
        event_type = event.get("type")
        
        if event_type == "thinking":
            print(f"🤔 Agente: Pensando... (iteración {event.get('iteration')})")
        
        elif event_type == "tool_call":
            tool = event.get("tool")
            args = event.get("arguments", {})
            print(f"🔧 Ejecutando: {tool}({', '.join(f'{k}={v}' for k, v in args.items())})")
        
        elif event_type == "tool_result":
            success = event.get("success")
            result = event.get("result")
            if success:
                print(f"✅ Resultado: {result}")
            else:
                error = event.get("error")
                print(f"❌ Error: {error}")
        
        elif event_type == "approval_required":
            tool = event.get("tool")
            print(f"⚠️  Requiere aprobación: {tool}")
            # En un sistema real, aquí pedirías confirmación al usuario
        
        elif event_type == "message":
            content = event.get("content")
            print(f"\n🤖 Agente: {content}")
        
        elif event_type == "error":
            error = event.get("error")
            print(f"❌ Error del agente: {error}")
        
        elif event_type == "done":
            iterations = event.get("iterations")
            print(f"\n✓ Completado en {iterations} iteración(es)")


async def example_streaming():
    """Ejemplo con streaming de respuesta"""
    
    print("\n" + "=" * 60)
    print("EJEMPLO: Streaming de Respuesta")
    print("=" * 60)
    
    config = AgentConfig(autonomy_level="full")  # Modo autónomo total
    llm = create_llm_provider("deepseek", model="deepseek-chat")
    agent = AgentCore(llm, config)
    
    # Registrar tools
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    print("\n👤 Usuario: Explica qué es Python en 2 párrafos\n")
    print("🤖 Agente: ", end="", flush=True)
    
    async for event in agent.process_message(
        "Explica qué es Python en 2 párrafos",
        "streaming_demo"
    ):
        if event.get("type") == "message":
            # En streaming real, esto vendría en chunks
            print(event.get("content"))


async def example_conversation_history():
    """Ejemplo mostrando memoria de conversación"""
    
    print("\n" + "=" * 60)
    print("EJEMPLO: Memoria de Conversación")
    print("=" * 60)
    
    config = AgentConfig(autonomy_level="semi")
    llm = create_llm_provider("deepseek")
    agent = AgentCore(llm, config)
    
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    conv_id = "memory_demo"
    
    # Primera pregunta
    await process_message(
        agent,
        "Crea un archivo llamado 'data.txt' con el número 42",
        conv_id
    )
    
    # Segunda pregunta que hace referencia a la anterior
    await process_message(
        agent,
        "Ahora lee ese archivo que acabas de crear",
        conv_id
    )
    
    # Mostrar historial
    print("\n📜 Historial de conversación:")
    history = agent.get_conversation_history(conv_id)
    for msg in history:
        role = msg["role"]
        content = msg["content"][:100]  # Primeros 100 chars
        print(f"  {role}: {content}...")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         AGENTE AUTÓNOMO - EJEMPLO DE USO                 ║
║         Basado en arquitectura Cline                     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Ejecutar ejemplo principal
    asyncio.run(main())
    
    # Descomentar para ver otros ejemplos:
    # asyncio.run(example_streaming())
    # asyncio.run(example_conversation_history())
