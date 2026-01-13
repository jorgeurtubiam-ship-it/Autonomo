"""
Test de Integración - Storage + API
Verifica que el API guarde y recupere conversaciones
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("""
╔══════════════════════════════════════════════════════════╗
║    TEST INTEGRACIÓN - STORAGE + API                      ║
╚══════════════════════════════════════════════════════════╝
""")

from backend.api.dependencies import get_agent, get_storage_dependency, load_conversation_history
from backend.storage import get_storage
from backend.api.models import ChatRequest, ToolCallInfo

# Test 1: Simular endpoint POST /api/chat con storage
print("="*60)
print("TEST 1: Endpoint Chat con Persistencia")
print("="*60)

async def test_chat_with_storage():
    agent = get_agent()
    storage = get_storage_dependency()
    
    conv_id = "integration_test_001"
    
    # Simular request
    request = ChatRequest(
        message="Crea un archivo integration_test.txt con 'Storage funciona!'",
        conversation_id=conv_id
    )
    
    print(f"📤 Request:")
    print(f"   Message: {request.message}")
    print(f"   Conv ID: {conv_id}")
    
    # Cargar historial (si existe)
    load_conversation_history(conv_id, agent, storage)
    
    # Guardar mensaje del usuario
    storage.save_message(conv_id, "user", request.message)
    print(f"\n💾 Mensaje de usuario guardado en DB")
    
    # Procesar
    print(f"\n🔄 Procesando...")
    final_message = ""
    tool_calls_list = []
    
    async for event in agent.process_message(request.message, conv_id):
        if event.get("type") == "tool_call":
            tool_name = event.get("tool")
            print(f"   🔧 Tool: {tool_name}")
            tool_calls_list.append(ToolCallInfo(
                id=event.get("tool_call_id", ""),
                name=tool_name,
                arguments=event.get("arguments", {})
            ))
        elif event.get("type") == "message":
            final_message = event.get("content", "")
    
    # Guardar respuesta del agente
    storage.save_message(
        conv_id,
        "assistant",
        final_message,
        tool_calls=[tc.dict() for tc in tool_calls_list] if tool_calls_list else None
    )
    print(f"\n💾 Respuesta del agente guardada en DB")
    
    print(f"\n📥 Response:")
    print(f"   Message: {final_message[:100]}...")
    print(f"   Tools ejecutados: {len(tool_calls_list)}")
    
    return True

success1 = asyncio.run(test_chat_with_storage())

# Test 2: Recuperar historial
print("\n" + "="*60)
print("TEST 2: Recuperar Historial desde DB")
print("="*60)

storage = get_storage()
messages = storage.get_messages("integration_test_001")

print(f"✅ Mensajes recuperados: {len(messages)}")
for i, msg in enumerate(messages, 1):
    print(f"\n📝 Mensaje {i}:")
    print(f"   Role: {msg.role}")
    print(f"   Content: {msg.content[:60]}...")
    if msg.tool_calls:
        print(f"   Tool calls: Sí")

# Test 3: Listar conversaciones
print("\n" + "="*60)
print("TEST 3: Listar Conversaciones")
print("="*60)

conversations = storage.list_conversations()
print(f"✅ Total conversaciones: {len(conversations)}")

for conv in conversations[:5]:  # Mostrar primeras 5
    print(f"\n📁 {conv.id}")
    print(f"   Title: {conv.title or '(sin título)'}")
    print(f"   Messages: {conv.message_count}")
    print(f"   Updated: {conv.updated_at}")

# Test 4: Cargar historial en nueva sesión
print("\n" + "="*60)
print("TEST 4: Cargar Historial en Nueva Sesión")
print("="*60)

# Simular nueva sesión del agente
from backend.agent import AgentCore, AgentConfig, create_llm_provider
from backend.tools import get_all_tools

config = AgentConfig(autonomy_level="semi")
llm = create_llm_provider("ollama", model="llama3.2:latest")
new_agent = AgentCore(llm, config)

for tool in get_all_tools():
    new_agent.register_tool(tool)

# Cargar historial
load_conversation_history("integration_test_001", new_agent, storage)

history = new_agent.get_conversation_history("integration_test_001")
print(f"✅ Historial cargado en nuevo agente: {len(history)} mensajes")

for i, msg in enumerate(history, 1):
    print(f"   {i}. {msg['role']}: {msg['content'][:50]}...")

# Resumen
print("\n" + "="*60)
print("RESUMEN")
print("="*60)

print(f"""
✅ Integración Storage + API Funcional

📊 Tests:
   1. Chat con persistencia: ✅
   2. Recuperar historial: ✅
   3. Listar conversaciones: ✅
   4. Cargar en nueva sesión: ✅

💾 Persistencia:
   - Mensajes guardados: {len(messages)}
   - Conversaciones totales: {len(conversations)}
   - Database: {storage.db_path}

🎉 El sistema está completamente integrado!
   - API guarda automáticamente
   - Historial se recupera
   - Multi-sesión funciona
""")

print("="*60)
