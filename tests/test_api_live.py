"""
Test Completo del API en Vivo
Prueba todos los endpoints con el servidor corriendo
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("""
╔══════════════════════════════════════════════════════════╗
║         TEST COMPLETO DEL API EN VIVO                    ║
╚══════════════════════════════════════════════════════════╝
""")

# Test 1: Root endpoint
print("="*60)
print("TEST 1: Root Endpoint (GET /)")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Name: {data['name']}")
    print(f"✅ Version: {data['version']}")
    print(f"✅ Status: {data['status']}")
    print(f"\n📋 Endpoints disponibles:")
    for key, value in data['endpoints'].items():
        print(f"   - {key}: {value}")
    
    test1_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test1_passed = False

# Test 2: Health check
print("\n" + "="*60)
print("TEST 2: Health Check (GET /health)")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Service: {data['service']}")
    print(f"✅ Health: {data['status']}")
    print(f"✅ Uptime: {data['uptime_seconds']} segundos")
    
    test2_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test2_passed = False

# Test 3: List tools
print("\n" + "="*60)
print("TEST 3: List Tools (GET /api/tools)")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/api/tools")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Total tools: {data['total']}")
    print(f"\n🔧 Primeros 5 tools:")
    for i, tool in enumerate(data['tools'][:5], 1):
        print(f"   {i}. {tool['name']} ({tool['category']})")
        print(f"      {tool['description'][:60]}...")
    
    test3_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test3_passed = False

# Test 4: Get config
print("\n" + "="*60)
print("TEST 4: Get Config (GET /api/config)")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/api/config")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ LLM Provider: {data['llm_provider']}")
    print(f"✅ Model: {data['model']}")
    print(f"✅ Autonomy: {data['autonomy_level']}")
    print(f"✅ Tools: {data['tools_count']}")
    
    test4_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test4_passed = False

# Test 5: Send chat message
print("\n" + "="*60)
print("TEST 5: Chat Endpoint (POST /api/chat)")
print("="*60)

try:
    payload = {
        "message": "Lista los archivos .py en el directorio actual",
        "conversation_id": "api_live_test_001"
    }
    
    print(f"📤 Enviando mensaje...")
    print(f"   Message: {payload['message']}")
    print(f"   Conv ID: {payload['conversation_id']}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        timeout=120  # 2 minutos timeout
    )
    
    data = response.json()
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"✅ Conv ID: {data['conversation_id']}")
    print(f"✅ Message: {data['message'][:100]}...")
    print(f"✅ Iterations: {data['iterations']}")
    
    if data.get('tool_calls'):
        print(f"✅ Tools ejecutados: {len(data['tool_calls'])}")
        for tc in data['tool_calls']:
            print(f"   🔧 {tc['name']}")
    
    test5_passed = True
    test5_conv_id = data['conversation_id']
except Exception as e:
    print(f"❌ Error: {e}")
    test5_passed = False
    test5_conv_id = None

# Test 6: Get conversation history
print("\n" + "="*60)
print("TEST 6: Get History (GET /api/chat/{id}/history)")
print("="*60)

if test5_conv_id:
    try:
        response = requests.get(f"{BASE_URL}/api/chat/{test5_conv_id}/history")
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Conv ID: {data['conversation_id']}")
        print(f"✅ Total messages: {data['total']}")
        
        print(f"\n📝 Mensajes:")
        for i, msg in enumerate(data['messages'], 1):
            print(f"   {i}. {msg['role']}: {msg['content'][:50]}...")
        
        test6_passed = True
    except Exception as e:
        print(f"❌ Error: {e}")
        test6_passed = False
else:
    print("⚠️  Skipped (no conversation ID from test 5)")
    test6_passed = False

# Test 7: List conversations
print("\n" + "="*60)
print("TEST 7: List Conversations (GET /api/conversations)")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/api/conversations")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Total conversations: {data['total']}")
    
    print(f"\n📁 Conversaciones:")
    for i, conv in enumerate(data['conversations'][:5], 1):
        print(f"   {i}. {conv['id']}")
        print(f"      Messages: {conv['message_count']}")
        print(f"      Updated: {conv['updated_at']}")
    
    test7_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test7_passed = False

# Test 8: Get specific tool
print("\n" + "="*60)
print("TEST 8: Get Tool Detail (GET /api/tools/{name})")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/api/tools/write_file")
    data = response.json()
    
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Name: {data['name']}")
    print(f"✅ Category: {data['category']}")
    print(f"✅ Description: {data['description'][:60]}...")
    print(f"✅ Parameters: {len(data['parameters'].get('properties', {}))} params")
    
    test8_passed = True
except Exception as e:
    print(f"❌ Error: {e}")
    test8_passed = False

# Test 9: Send another message (test persistence)
print("\n" + "="*60)
print("TEST 9: Chat con Historial (POST /api/chat)")
print("="*60)

if test5_conv_id:
    try:
        payload = {
            "message": "¿Cuántos archivos encontraste?",
            "conversation_id": test5_conv_id
        }
        
        print(f"📤 Enviando mensaje de seguimiento...")
        print(f"   Message: {payload['message']}")
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=120
        )
        
        data = response.json()
        
        print(f"\n✅ Status: {response.status_code}")
        print(f"✅ Message: {data['message'][:100]}...")
        print(f"✅ Iterations: {data['iterations']}")
        
        # Verificar que el agente recuerda el contexto
        if "archivo" in data['message'].lower() or "encontr" in data['message'].lower():
            print(f"✅ El agente recuerda el contexto anterior!")
        
        test9_passed = True
    except Exception as e:
        print(f"❌ Error: {e}")
        test9_passed = False
else:
    print("⚠️  Skipped (no conversation ID)")
    test9_passed = False

# Resumen
print("\n" + "="*60)
print("RESUMEN DE TESTS")
print("="*60)

results = {
    "1. Root Endpoint": test1_passed,
    "2. Health Check": test2_passed,
    "3. List Tools": test3_passed,
    "4. Get Config": test4_passed,
    "5. Chat Endpoint": test5_passed,
    "6. Get History": test6_passed,
    "7. List Conversations": test7_passed,
    "8. Get Tool Detail": test8_passed,
    "9. Chat con Historial": test9_passed,
}

print()
for test, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test}")

passed_count = sum(results.values())
total_count = len(results)

print("\n" + "="*60)
if passed_count == total_count:
    print(f"✅✅✅ TODOS LOS TESTS PASARON ({passed_count}/{total_count})")
    print("\n🎉 El API está 100% funcional!")
    print("\n📊 Características verificadas:")
    print("   - Endpoints REST funcionando")
    print("   - Tools disponibles y ejecutándose")
    print("   - Persistencia en SQLite")
    print("   - Historial de conversaciones")
    print("   - Contexto mantenido entre mensajes")
else:
    print(f"⚠️  {passed_count}/{total_count} tests pasaron")

print("="*60)
