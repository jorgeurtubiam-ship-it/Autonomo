"""
Test del Agente Completo con Ollama
Prueba el ciclo Plan & Act con IA real
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.agent import AgentCore, AgentConfig, create_llm_provider
from backend.tools import get_all_tools


async def test_agent_with_ollama():
    """Test del agente completo usando Ollama"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║        TEST DEL AGENTE COMPLETO CON OLLAMA               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("🔧 Configurando agente...")
    
    # 1. Crear configuración
    config = AgentConfig(
        autonomy_level="full",  # Modo autónomo para el test
        max_iterations=5
    )
    
    # 2. Crear LLM con Ollama
    print("🤖 Conectando con Ollama (llama3.2:1b)...")
    llm = create_llm_provider(
        "ollama",
        model="llama3.2:1b",
        base_url="http://localhost:11434"
    )
    
    # 3. Crear agente
    agent = AgentCore(llm, config)
    
    # 4. Registrar tools
    print("📦 Registrando tools...")
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    tools_count = len(agent.tool_registry.list_tools())
    print(f"✅ {tools_count} tools registrados\n")
    
    # 5. Test simple: Crear un archivo
    print("="*60)
    print("TEST 1: Crear un archivo")
    print("="*60)
    
    conversation_id = "ollama_test_001"
    user_message = "Crea un archivo llamado 'ollama_test.txt' con el texto 'Hola desde Ollama'"
    
    print(f"\n👤 Usuario: {user_message}\n")
    
    async for event in agent.process_message(user_message, conversation_id):
        event_type = event.get("type")
        
        if event_type == "thinking":
            iteration = event.get("iteration", 0)
            print(f"🤔 Agente pensando... (iteración {iteration})")
        
        elif event_type == "tool_call":
            tool = event.get("tool")
            args = event.get("arguments", {})
            print(f"🔧 Ejecutando: {tool}")
            print(f"   Argumentos: {args}")
        
        elif event_type == "tool_result":
            success = event.get("success")
            if success:
                result = event.get("result", {})
                print(f"✅ Tool ejecutado exitosamente")
                if isinstance(result, dict) and 'path' in result:
                    print(f"   Archivo: {result.get('path')}")
            else:
                error = event.get("error")
                print(f"❌ Error: {error}")
        
        elif event_type == "message":
            content = event.get("content")
            print(f"\n🤖 Agente: {content}\n")
        
        elif event_type == "error":
            error = event.get("error")
            print(f"❌ Error del agente: {error}")
        
        elif event_type == "done":
            iterations = event.get("iterations")
            print(f"✓ Completado en {iterations} iteración(es)")
    
    # 6. Verificar que el archivo se creó
    print("\n" + "="*60)
    print("VERIFICACIÓN")
    print("="*60)
    
    import os
    if os.path.exists("ollama_test.txt"):
        with open("ollama_test.txt", "r") as f:
            content = f.read()
        print(f"✅ Archivo creado correctamente")
        print(f"   Contenido: {content}")
    else:
        print("❌ El archivo no se creó")
    
    # 7. Test 2: Listar archivos
    print("\n" + "="*60)
    print("TEST 2: Listar archivos")
    print("="*60)
    
    user_message2 = "Lista los archivos en el directorio actual"
    print(f"\n👤 Usuario: {user_message2}\n")
    
    async for event in agent.process_message(user_message2, conversation_id):
        if event.get("type") == "message":
            print(f"🤖 Agente: {event.get('content')}\n")
        elif event.get("type") == "tool_call":
            print(f"🔧 Ejecutando: {event.get('tool')}")
    
    print("\n" + "="*60)
    print("✅ TESTS CON OLLAMA COMPLETADOS")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(test_agent_with_ollama())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
