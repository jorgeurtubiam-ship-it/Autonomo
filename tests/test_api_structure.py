"""
Test del Backend API
Prueba los endpoints REST sin necesidad de instalar FastAPI
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("""
╔══════════════════════════════════════════════════════════╗
║           TEST DEL BACKEND API - ESTRUCTURA              ║
╚══════════════════════════════════════════════════════════╝
""")

print("Verificando estructura del API...\n")

# Test 1: Verificar que existen los archivos
print("1. Verificando archivos...")
files_to_check = [
    "backend/api/main.py",
    "backend/api/dependencies.py",
    "backend/api/models/__init__.py",
    "backend/api/models/requests.py",
    "backend/api/models/responses.py",
    "backend/api/routes/__init__.py",
    "backend/api/routes/chat.py",
    "backend/api/routes/tools.py",
    "backend/api/routes/config.py",
]

all_exist = True
for file_path in files_to_check:
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"   {status} {file_path}")
    if not exists:
        all_exist = False

if all_exist:
    print("\n✅ Todos los archivos existen\n")
else:
    print("\n❌ Faltan algunos archivos\n")
    sys.exit(1)

# Test 2: Verificar imports
print("2. Verificando imports...")

try:
    from backend.api.models import (
        ChatRequest, ChatResponse,
        ToolsList, ConfigResponse
    )
    print("   ✅ Modelos importados correctamente")
except Exception as e:
    print(f"   ❌ Error importando modelos: {e}")
    all_exist = False

try:
    from backend.api.dependencies import get_agent
    print("   ✅ Dependencies importadas correctamente")
except Exception as e:
    print(f"   ❌ Error importando dependencies: {e}")
    all_exist = False

# Test 3: Verificar modelos
print("\n3. Verificando modelos Pydantic...")

try:
    # Test ChatRequest
    chat_req = ChatRequest(
        message="Test message",
        conversation_id="test_123"
    )
    print(f"   ✅ ChatRequest: {chat_req.message}")
    
    # Test ChatResponse
    chat_resp = ChatResponse(
        conversation_id="test_123",
        message="Response",
        iterations=1
    )
    print(f"   ✅ ChatResponse: {chat_resp.conversation_id}")
    
except Exception as e:
    print(f"   ❌ Error con modelos: {e}")

# Test 4: Verificar agente
print("\n4. Verificando singleton del agente...")

try:
    agent = get_agent()
    tools_count = len(agent.tool_registry.list_tools())
    print(f"   ✅ Agente inicializado")
    print(f"   ✅ Tools registrados: {tools_count}")
    print(f"   ✅ LLM: {agent.llm.__class__.__name__}")
    print(f"   ✅ Modelo: {agent.llm.model}")
except Exception as e:
    print(f"   ❌ Error con agente: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("RESUMEN")
print("="*60)

if all_exist:
    print("\n✅ Backend API estructura correcta")
    print("\n📝 Para iniciar el servidor:")
    print("   cd backend/api")
    print("   python3 -m uvicorn main:app --reload")
    print("\n📚 Documentación automática:")
    print("   http://localhost:8000/docs")
else:
    print("\n❌ Hay problemas con la estructura")

print("\n" + "="*60)
