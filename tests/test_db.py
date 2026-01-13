#!/usr/bin/env python3
"""
Test completo de la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage import ConversationStorage
import uuid

def test_database():
    print("🧪 Test de Base de Datos\n")
    
    # 1. Crear storage
    print("1️⃣ Creando storage...")
    storage = ConversationStorage()
    print("   ✅ Storage creado\n")
    
    # 2. Test: Crear conversación
    print("2️⃣ Test: Crear conversación...")
    conv_id = str(uuid.uuid4())
    storage.create_conversation(conv_id, "Test Conversation")
    print(f"   ✅ Conversación creada: {conv_id}\n")
    
    # 3. Test: Guardar mensaje
    print("3️⃣ Test: Guardar mensaje...")
    storage.save_message(conv_id, "user", "Hola, esto es un test")
    print("   ✅ Mensaje guardado\n")
    
    # 4. Test: Obtener mensajes
    print("4️⃣ Test: Obtener mensajes...")
    messages = storage.get_messages(conv_id)
    print(f"   ✅ Mensajes obtenidos: {len(messages)}")
    for msg in messages:
        print(f"      - {msg.role}: {msg.content[:50]}...\n")
    
    # 5. Test: Listar conversaciones
    print("5️⃣ Test: Listar conversaciones...")
    conversations = storage.list_conversations(limit=10)
    print(f"   ✅ Conversaciones: {len(conversations)}")
    for conv in conversations[:3]:
        print(f"      - {conv.title} ({conv.message_count} mensajes)\n")
    
    # 6. Test: Guardar API key
    print("6️⃣ Test: Guardar API key...")
    try:
        if hasattr(storage, 'save_api_key'):
            storage.save_api_key("test_provider", "sk-test-123")
            print("   ✅ API key guardada\n")
            
            # 7. Test: Obtener API key
            print("7️⃣ Test: Obtener API key...")
            api_key = storage.get_api_key("test_provider")
            print(f"   ✅ API key obtenida: {api_key[:10]}...\n")
        else:
            print("   ❌ Método save_api_key NO EXISTE\n")
            print("   📋 Métodos disponibles:")
            methods = [m for m in dir(storage) if not m.startswith('_') and callable(getattr(storage, m))]
            for m in sorted(methods):
                print(f"      - {m}")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("\n✅ Test completado!")

if __name__ == "__main__":
    test_database()
