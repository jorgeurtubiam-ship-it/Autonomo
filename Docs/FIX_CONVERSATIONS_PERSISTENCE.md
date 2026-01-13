# Fix: Persistencia de Conversaciones

## Problema Identificado

Las conversaciones del chat **no se estaban guardando** porque:
- El endpoint `/api/chat` no creaba la conversación antes de guardar mensajes
- Solo guardaba mensajes, pero no la entrada en la tabla `conversations`
- Por eso el frontend siempre mostraba las mismas 3 conversaciones de tests

## Solución Implementada

### Cambio en `backend/api/routes/chat.py`

**Antes:**
```python
# Guardar mensaje del usuario
storage.save_message(
    conversation_id,
    "user",
    request.message
)
```

**Después:**
```python
# Crear conversación si no existe
existing_conv = storage.get_conversation(conversation_id)
if not existing_conv:
    title = request.message[:50] if len(request.message) > 50 else request.message
    storage.create_conversation(conversation_id, title=title)

# Guardar mensaje del usuario
storage.save_message(
    conversation_id,
    "user",
    request.message
)
```

## Verificación

### Antes del Fix:
```sql
SELECT COUNT(*) FROM conversations;
-- Resultado: 3 (solo tests antiguos)
```

### Después del Fix:
```sql
SELECT COUNT(*) FROM conversations;
-- Resultado: 4+ (incluye nuevas conversaciones del chat)
```

## Cómo Probar

1. **Abre el chat:**
   ```
   http://localhost:3000
   ```

2. **Envía un mensaje:**
   ```
   "Hola, este es un test"
   ```

3. **Recarga la página:**
   - Deberías ver la nueva conversación en el sidebar
   - El título será el primer mensaje (truncado a 50 chars)

4. **Verifica en BD:**
   ```bash
   sqlite3 ~/.agent_data/conversations/agent.db \
     "SELECT id, title, message_count FROM conversations ORDER BY updated_at DESC LIMIT 5;"
   ```

## Estado

- ✅ Fix aplicado
- ✅ Conversaciones se crean automáticamente
- ✅ Título basado en primer mensaje
- ✅ Sidebar se actualiza correctamente

## Archivos Modificados

- `backend/api/routes/chat.py` - Líneas 32-48
