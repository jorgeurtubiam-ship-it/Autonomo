"""
Test del Agente con llama3.2:latest
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.agent import AgentCore, AgentConfig, create_llm_provider
from backend.tools import get_all_tools


async def test_with_llama32():
    """Test con llama3.2:latest"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║      TEST CON LLAMA3.2:LATEST - TOOL CALLING             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("🔧 Configurando agente...")
    
    config = AgentConfig(
        autonomy_level="full",
        max_iterations=5
    )
    
    print("🤖 Conectando con Ollama (llama3.2:latest)...")
    llm = create_llm_provider(
        "ollama",
        model="llama3.2:latest",
        base_url="http://localhost:11434"
    )
    
    agent = AgentCore(llm, config)
    
    print("📦 Registrando tools...")
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    print(f"✅ {len(agent.tool_registry.list_tools())} tools registrados\n")
    
    # Test: Crear archivo
    print("="*60)
    print("TEST: Crear archivo con llama3.2:latest")
    print("="*60)
    
    conversation_id = "llama32_test"
    message = "Crea un archivo llamado 'test_llama32.txt' con el contenido 'Test exitoso con llama3.2'"
    
    print(f"\n👤 Usuario: {message}\n")
    
    tool_executed = False
    
    async for event in agent.process_message(message, conversation_id):
        event_type = event.get("type")
        
        if event_type == "thinking":
            print(f"🤔 Pensando... (iteración {event.get('iteration')})")
        
        elif event_type == "tool_call":
            tool_executed = True
            tool = event.get("tool")
            args = event.get("arguments", {})
            print(f"🔧 ¡TOOL EJECUTADO! {tool}")
            print(f"   Args: {args}")
        
        elif event_type == "tool_result":
            success = event.get("success")
            result = event.get("result", {})
            if success:
                print(f"✅ Tool exitoso")
                if isinstance(result, dict):
                    for key, value in result.items():
                        if key not in ['success']:
                            print(f"   {key}: {value}")
            else:
                print(f"❌ Error: {event.get('error')}")
        
        elif event_type == "message":
            print(f"\n🤖 Respuesta: {event.get('content')}\n")
        
        elif event_type == "done":
            print(f"✓ Completado en {event.get('iterations')} iteración(es)")
    
    # Verificar
    print("\n" + "="*60)
    print("VERIFICACIÓN")
    print("="*60)
    
    if tool_executed:
        print("✅ El LLM SÍ ejecutó tools (soporta tool calling)")
    else:
        print("❌ El LLM NO ejecutó tools (no soporta tool calling)")
    
    if os.path.exists("test_llama32.txt"):
        with open("test_llama32.txt", "r") as f:
            content = f.read()
        print(f"✅ Archivo creado: test_llama32.txt")
        print(f"   Contenido: {content}")
    else:
        print("❌ Archivo no creado")
    
    print("\n" + "="*60)
    print("FIN DEL TEST")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(test_with_llama32())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
