# Fix: Error al Cambiar Provider

## ❌ Problema Identificado

**Error:** "Error cambiando provider: Error en la respuesta"

**Causa:** El endpoint `POST /api/config/` no existía en el backend.

**Síntomas:**
- Al cambiar de Ollama a DeepSeek → Error
- Vuelve automáticamente a Ollama
- Mensaje de error en el chat

---

## ✅ Solución Implementada

### Agregado POST Endpoint en `backend/api/routes/config.py`

**Funcionalidad:**
```python
@router.post("/")
async def update_config(request: dict, config: dict):
    # Actualiza provider
    # Guarda API keys
    # Cambia modelo según provider
    # Retorna confirmación
```

**Soporta:**
- ✅ Cambio de provider (ollama, openai, anthropic, deepseek)
- ✅ Guardado de API keys
- ✅ Cambio de modelo
- ✅ Cambio de temperatura y max_tokens

---

## 🎯 Cómo Funciona Ahora

### 1. Cambiar Provider:
```javascript
POST /api/config/
{
  "llm_provider": "deepseek"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Configuración actualizada",
  "config": {
    "llm_provider": "deepseek",
    "model": "deepseek-chat"
  }
}
```

### 2. Guardar API Keys:
```javascript
POST /api/config/
{
  "api_keys": {
    "openai": "sk-...",
    "anthropic": "sk-ant-...",
    "deepseek": "sk-..."
  }
}
```

### 3. Cambiar Provider + API Key:
```javascript
POST /api/config/
{
  "llm_provider": "deepseek",
  "api_keys": {
    "deepseek": "sk-..."
  }
}
```

---

## 🔄 Modelos por Provider

**Ollama:**
- Modelo: `llama3.2:latest`

**OpenAI:**
- Modelo: `gpt-4`

**Anthropic:**
- Modelo: `claude-3-sonnet-20240229`

**DeepSeek:**
- Modelo: `deepseek-chat`

---

## ✅ Testing

**Cambiar a DeepSeek:**
```bash
curl -X POST http://localhost:8000/api/config/ \
  -H "Content-Type: application/json" \
  -d '{"llm_provider": "deepseek"}'
```

**Verificar cambio:**
```bash
curl http://localhost:8000/api/config/
```

**Resultado esperado:**
```json
{
  "llm_provider": "deepseek",
  "model": "deepseek-chat",
  ...
}
```

---

## 🎉 Ahora Funciona

**En el frontend:**
1. Selecciona "DeepSeek" en el dropdown
2. ✅ Se cambia correctamente
3. ✅ Mensaje: "Provider cambiado a deepseek"
4. ✅ No más errores

**API Keys:**
1. Click en 🔑
2. Ingresa las keys
3. Click en "Guardar"
4. ✅ Se guardan correctamente
5. ✅ Mensaje: "API Keys guardadas correctamente"

---

## 📁 Archivo Modificado

- `backend/api/routes/config.py` - Agregado POST endpoint

---

## 🔧 Próximos Pasos

**Para usar DeepSeek:**
1. Recarga la página (Cmd+Shift+R)
2. Click en 🔑
3. Ingresa tu DeepSeek API key
4. Guarda
5. Selecciona "DeepSeek" en el dropdown
6. ✅ Funcionando!

---

**Estado:** ✅ ARREGLADO
**Fecha:** 2025-12-25
