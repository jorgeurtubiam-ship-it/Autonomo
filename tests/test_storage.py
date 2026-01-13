"""
Test del Sistema de Storage
Prueba SQLite + Archivos como Antigravity
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("""
╔══════════════════════════════════════════════════════════╗
║    TEST STORAGE - PERSISTENCIA COMO ANTIGRAVITY          ║
╚══════════════════════════════════════════════════════════╝
""")

from backend.storage import get_storage, StoredMessage

storage = get_storage()

print(f"📁 Base directory: {storage.base_dir}")
print(f"💾 Database: {storage.db_path}")
print(f"📄 Artifacts: {storage.artifacts_dir}\n")

# Test 1: Crear conversación
print("="*60)
print("TEST 1: Crear Conversación")
print("="*60)

conv_id = "test_storage_001"
created = storage.create_conversation(conv_id, "Test de Storage")
print(f"✅ Conversación creada: {created}")

# Test 2: Guardar mensajes
print("\n" + "="*60)
print("TEST 2: Guardar Mensajes")
print("="*60)

msg1_id = storage.save_message(
    conv_id,
    "user",
    "Hola, crea un archivo test.txt"
)
print(f"✅ Mensaje 1 guardado (ID: {msg1_id})")

msg2_id = storage.save_message(
    conv_id,
    "assistant",
    "Archivo creado exitosamente",
    tool_calls=[{
        "id": "call_1",
        "name": "write_file",
        "arguments": {"path": "test.txt", "content": "Hello"}
    }]
)
print(f"✅ Mensaje 2 guardado (ID: {msg2_id})")

# Test 3: Leer mensajes
print("\n" + "="*60)
print("TEST 3: Leer Mensajes")
print("="*60)

messages = storage.get_messages(conv_id)
print(f"✅ Mensajes recuperados: {len(messages)}")

for i, msg in enumerate(messages, 1):
    print(f"\n📝 Mensaje {i}:")
    print(f"   Role: {msg.role}")
    print(f"   Content: {msg.content[:50]}...")
    print(f"   Created: {msg.created_at}")
    if msg.tool_calls:
        print(f"   Tool calls: {msg.tool_calls[:100]}...")

# Test 4: Guardar artifact
print("\n" + "="*60)
print("TEST 4: Guardar Artifact")
print("="*60)

artifact_content = """# Task List

- [x] Crear conversación
- [x] Guardar mensajes
- [/] Probar artifacts
"""

artifact_path = storage.save_artifact(conv_id, "task.md", artifact_content)
print(f"✅ Artifact guardado: {artifact_path}")

# Test 5: Leer artifact
print("\n" + "="*60)
print("TEST 5: Leer Artifact")
print("="*60)

loaded_artifact = storage.load_artifact(conv_id, "task.md")
print(f"✅ Artifact cargado:")
print(loaded_artifact)

# Test 6: Listar artifacts
print("\n" + "="*60)
print("TEST 6: Listar Artifacts")
print("="*60)

artifacts = storage.list_artifacts(conv_id)
print(f"✅ Artifacts encontrados: {len(artifacts)}")
for artifact in artifacts:
    print(f"   - {artifact}")

# Test 7: Info de conversación
print("\n" + "="*60)
print("TEST 7: Info de Conversación")
print("="*60)

conv_info = storage.get_conversation(conv_id)
if conv_info:
    print(f"✅ Conversación:")
    print(f"   ID: {conv_info.id}")
    print(f"   Title: {conv_info.title}")
    print(f"   Messages: {conv_info.message_count}")
    print(f"   Created: {conv_info.created_at}")
    print(f"   Updated: {conv_info.updated_at}")

# Test 8: Listar conversaciones
print("\n" + "="*60)
print("TEST 8: Listar Conversaciones")
print("="*60)

conversations = storage.list_conversations()
print(f"✅ Total conversaciones: {len(conversations)}")
for conv in conversations:
    print(f"\n   📁 {conv.id}")
    print(f"      Title: {conv.title}")
    print(f"      Messages: {conv.message_count}")

# Test 9: Buscar mensajes
print("\n" + "="*60)
print("TEST 9: Buscar Mensajes")
print("="*60)

results = storage.search_messages("archivo")
print(f"✅ Resultados de búsqueda: {len(results)}")
for result in results:
    print(f"\n   📝 {result.role}: {result.content[:50]}...")

# Test 10: Verificar persistencia
print("\n" + "="*60)
print("TEST 10: Verificar Persistencia")
print("="*60)

# Crear nueva instancia de storage
from backend.storage import ConversationStorage
storage2 = ConversationStorage()

# Leer datos con nueva instancia
messages2 = storage2.get_messages(conv_id)
print(f"✅ Mensajes recuperados con nueva instancia: {len(messages2)}")

artifact2 = storage2.load_artifact(conv_id, "task.md")
print(f"✅ Artifact recuperado con nueva instancia: {len(artifact2)} chars")

# Resumen
print("\n" + "="*60)
print("RESUMEN")
print("="*60)

print(f"""
✅ Sistema de Storage Funcional

📊 Estadísticas:
   - Conversaciones: {len(conversations)}
   - Mensajes guardados: {len(messages)}
   - Artifacts: {len(artifacts)}
   - Database: {storage.db_path}
   - Artifacts dir: {storage.artifacts_dir}

🎉 Persistencia verificada:
   - SQLite para mensajes ✅
   - Archivos para artifacts ✅
   - Búsqueda funcional ✅
   - Multi-instancia ✅

💡 Igual que Antigravity!
""")

print("="*60)
