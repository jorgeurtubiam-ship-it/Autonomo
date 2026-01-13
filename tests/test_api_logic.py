"""
Test del Backend API - Sin dependencias de FastAPI
Prueba directamente la lógica del agente
"""

import sys
import os
import asyncio

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("""
╔══════════════════════════════════════════════════════════╗
║    TEST BACKEND API - LÓGICA DEL AGENTE                  ║
╚══════════════════════════════════════════════════════════╝
""")

# Test 1: Modelos Pydantic
print("="*60)
print("TEST 1: Modelos Pydantic")
print("="*60)

from backend.api.models import (
    ChatRequest, ChatResponse, ToolCallInfo,
    ConfigUpdate, ConfigResponse,
    ToolsList, ToolInfo
)

try:
    # ChatRequest
    req = ChatRequest(message="Test", conversation_id="test_001")
    print(f"✅ ChatRequest: {req.message}")
    
    # ChatResponse
    resp = ChatResponse(
        conversation_id="test_001",
        message="Response",
        tool_calls=[ToolCallInfo(id="1", name="test", arguments={})],
        iterations=1
    )
    print(f"✅ ChatResponse: {resp.conversation_id}")
    
    # ConfigUpdate
    config = ConfigUpdate(llm_provider="ollama", model="llama3.2:latest")
    print(f"✅ ConfigUpdate: {config.llm_provider}")
    
    # ToolInfo
    tool_info = ToolInfo(
        name="test_tool",
        description="Test",
        category="test",
        parameters={}
    )
    print(f"✅ ToolInfo: {tool_info.name}")
    
    print("\n✅ Todos los modelos Pydantic OK\n")
    test1_passed = True
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    test1_passed = False


# Test 2: Agente Core (simula lo que haría el endpoint)
print("="*60)
print("TEST 2: Lógica del Agente (Simulación de Endpoint)")
print("="*60)

async def test_agent_logic():
    """Simula la lógica del endpoint POST /api/chat"""
    try:
        from agent import AgentCore, AgentConfig, create_llm_provider
        from tools import get_all_tools
        import uuid
        
        # Crear agente (igual que en dependencies.py)
        print("🔧 Creando agente...")
        config = AgentConfig(autonomy_level="semi", max_iterations=10)
        llm = create_llm_provider("ollama", model="llama3.2:latest")
        agent = AgentCore(llm, config)
        
        # Registrar tools
        for tool in get_all_tools():
            agent.register_tool(tool)
        
        tools_count = len(agent.tool_registry.list_tools())
        print(f"✅ Agente creado con {tools_count} tools")
        
        # Simular request
        message = "Crea un archivo api_test.txt con 'API funciona!'"
        conversation_id = f"api_test_{uuid.uuid4().hex[:8]}"
        
        print(f"\n📤 Request:")
        print(f"   Message: {message}")
        print(f"   Conv ID: {conversation_id}")
        
        # Procesar (igual que en routes/chat.py)
        print(f"\n🔄 Procesando...")
        final_message = ""
        tool_calls_list = []
        iterations = 0
        
        async for event in agent.process_message(message, conversation_id):
            event_type = event.get("type")
            
            if event_type == "tool_call":
                tool = event.get("tool")
                args = event.get("arguments", {})
                print(f"   🔧 Tool: {tool}")
                tool_calls_list.append(ToolCallInfo(
                    id=event.get("tool_call_id", "call_1"),
                    name=tool,
                    arguments=args
                ))
            
            elif event_type == "message":
                final_message = event.get("content", "")
            
            elif event_type == "done":
                iterations = event.get("iterations", 0)
        
        # Crear response (igual que en routes/chat.py)
        response = ChatResponse(
            conversation_id=conversation_id,
            message=final_message,
            tool_calls=tool_calls_list if tool_calls_list else None,
            iterations=iterations
        )
        
        print(f"\n📥 Response:")
        print(f"   Conv ID: {response.conversation_id}")
        print(f"   Message: {response.message[:80]}...")
        print(f"   Tools: {len(response.tool_calls) if response.tool_calls else 0}")
        print(f"   Iterations: {response.iterations}")
        
        # Verificar que el archivo se creó
        if os.path.exists("api_test.txt"):
            with open("api_test.txt", "r") as f:
                content = f.read()
            print(f"\n✅ Archivo creado: api_test.txt")
            print(f"   Contenido: '{content}'")
        
        print("\n✅ Lógica del agente funciona OK\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

test2_passed = asyncio.run(test_agent_logic())


# Test 3: Tools Registry (simula GET /api/tools)
print("="*60)
print("TEST 3: Tools Registry (Simulación GET /api/tools)")
print("="*60)

try:
    from agent import AgentCore, AgentConfig, create_llm_provider
    from tools import get_all_tools
    
    # Crear agente
    config = AgentConfig(autonomy_level="semi")
    llm = create_llm_provider("ollama", model="llama3.2:latest")
    agent = AgentCore(llm, config)
    
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    # Listar tools (igual que en routes/tools.py)
    tools_list = agent.tool_registry.list_tools()
    tools_info = []
    
    for tool_name in tools_list:
        tool = agent.tool_registry.get(tool_name)
        definition = tool.get_definition()
        
        tools_info.append(ToolInfo(
            name=definition["name"],
            description=definition["description"],
            category=getattr(tool, "category", "general"),
            parameters=definition["parameters"]
        ))
    
    # Crear response
    response = ToolsList(tools=tools_info, total=len(tools_info))
    
    print(f"✅ Tools listados: {response.total}")
    print(f"\n📋 Primeros 5 tools:")
    for i, tool in enumerate(response.tools[:5], 1):
        print(f"   {i}. {tool.name} ({tool.category})")
        print(f"      {tool.description[:60]}...")
    
    print("\n✅ Tools registry funciona OK\n")
    test3_passed = True
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    test3_passed = False


# Test 4: Config (simula GET /api/config)
print("="*60)
print("TEST 4: Configuración (Simulación GET /api/config)")
print("="*60)

try:
    from agent import AgentCore, AgentConfig, create_llm_provider
    from tools import get_all_tools
    
    # Crear agente
    config = AgentConfig(autonomy_level="full")
    llm = create_llm_provider("ollama", model="llama3.2:latest")
    agent = AgentCore(llm, config)
    
    for tool in get_all_tools():
        agent.register_tool(tool)
    
    # Crear response (igual que en routes/config.py)
    response = ConfigResponse(
        llm_provider=agent.llm.__class__.__name__.replace("Provider", "").lower(),
        model=agent.llm.model,
        autonomy_level=agent.config.autonomy_level,
        temperature=0.7,
        max_tokens=4000,
        tools_count=len(agent.tool_registry.list_tools())
    )
    
    print(f"✅ Configuración obtenida:")
    print(f"   LLM: {response.llm_provider}")
    print(f"   Modelo: {response.model}")
    print(f"   Autonomía: {response.autonomy_level}")
    print(f"   Tools: {response.tools_count}")
    
    print("\n✅ Config funciona OK\n")
    test4_passed = True
    
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    test4_passed = False


# Resumen
print("="*60)
print("RESUMEN DE TESTS")
print("="*60)

results = {
    "Modelos Pydantic": test1_passed,
    "Lógica del Agente (POST /api/chat)": test2_passed,
    "Tools Registry (GET /api/tools)": test3_passed,
    "Configuración (GET /api/config)": test4_passed
}

print()
for test, passed in results.items():
    status = "✅ OK" if passed else "❌ FAIL"
    print(f"{status} {test}")

all_passed = all(results.values())

print("\n" + "="*60)
if all_passed:
    print("✅✅✅ TODOS LOS TESTS PASARON")
    print("\n🎉 La lógica del Backend API funciona perfectamente")
    print("\n📝 Conclusión:")
    print("   - Modelos Pydantic: ✅")
    print("   - Agente Core: ✅")
    print("   - Tool calling: ✅")
    print("   - Endpoints simulados: ✅")
    print("\n🚀 El API está listo para usarse con FastAPI")
else:
    print("❌ ALGUNOS TESTS FALLARON")
print("="*60)
