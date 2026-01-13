"""
Test con timeout extendido (3 minutos)
Para modelos lentos de Ollama
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.agent import AgentCore, AgentConfig, create_llm_provider
from backend.tools import get_all_tools


async def test_with_extended_timeout():
    """Test con timeout de 3 minutos"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║    TEST CON TIMEOUT EXTENDIDO (3 MINUTOS)                ║
║    Modelo: llama3.2:latest                               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("🔧 Configurando agente...")
    print("⏱️  Timeout: 3 minutos por respuesta\n")
    
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
    
    # Test 1: Crear archivo
    print("="*60)
    print("TEST 1: Crear archivo")
    print("="*60)
    
    conversation_id = "extended_timeout_test"
    message = "Crea un archivo llamado 'success_test.txt' con el texto 'Tool calling funciona!'"
    
    print(f"\n👤 Usuario: {message}\n")
    print("⏳ Esperando respuesta del LLM (puede tomar hasta 3 minutos)...\n")
    
    tool_executed = False
    file_created = False
    
    async for event in agent.process_message(message, conversation_id):
        event_type = event.get("type")
        
        if event_type == "thinking":
            print(f"🤔 Pensando... (iteración {event.get('iteration')})")
        
        elif event_type == "tool_call":
            tool_executed = True
            tool = event.get("tool")
            args = event.get("arguments", {})
            print(f"\n🔧 ¡TOOL EJECUTADO! → {tool}")
            print(f"   Argumentos:")
            for key, value in args.items():
                print(f"      {key}: {value}")
        
        elif event_type == "tool_result":
            success = event.get("success")
            result = event.get("result", {})
            if success:
                print(f"✅ Tool ejecutado exitosamente")
                if isinstance(result, dict):
                    if 'path' in result:
                        file_created = True
                        print(f"   📄 Archivo: {result['path']}")
                    if 'size' in result:
                        print(f"   📊 Tamaño: {result['size']} bytes")
            else:
                print(f"❌ Error: {event.get('error')}")
        
        elif event_type == "message":
            content = event.get('content')
            print(f"\n🤖 Respuesta del agente:")
            print(f"   {content}\n")
        
        elif event_type == "done":
            iterations = event.get('iterations')
            print(f"\n✓ Completado en {iterations} iteración(es)")
    
    # Verificación
    print("\n" + "="*60)
    print("VERIFICACIÓN FINAL")
    print("="*60)
    
    print(f"\n1. Tool calling:")
    if tool_executed:
        print("   ✅ El LLM ejecutó tools correctamente")
    else:
        print("   ❌ El LLM NO ejecutó tools")
    
    print(f"\n2. Archivo creado:")
    if os.path.exists("success_test.txt"):
        with open("success_test.txt", "r") as f:
            content = f.read()
        print(f"   ✅ Archivo existe: success_test.txt")
        print(f"   📝 Contenido: '{content}'")
    else:
        print("   ❌ Archivo no existe")
    
    # Test 2: Listar archivos
    print("\n" + "="*60)
    print("TEST 2: Listar archivos")
    print("="*60)
    
    message2 = "Lista los archivos .txt en el directorio actual"
    print(f"\n👤 Usuario: {message2}\n")
    
    async for event in agent.process_message(message2, conversation_id):
        if event.get("type") == "tool_call":
            print(f"🔧 Ejecutando: {event.get('tool')}")
        elif event.get("type") == "message":
            print(f"\n🤖 {event.get('content')}\n")
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    if tool_executed and file_created:
        print("\n✅✅✅ ¡ÉXITO TOTAL!")
        print("   - Tool calling: FUNCIONA")
        print("   - Archivo creado: SÍ")
        print("   - Agente completamente funcional")
    elif tool_executed:
        print("\n✅ Tool calling funciona")
        print("❌ Pero el archivo no se creó correctamente")
    else:
        print("\n❌ Tool calling no funcionó")
        print("   Posibles causas:")
        print("   - Modelo no soporta function calling")
        print("   - Necesita más tiempo")
        print("   - Formato de tools incorrecto")


if __name__ == "__main__":
    try:
        asyncio.run(test_with_extended_timeout())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
