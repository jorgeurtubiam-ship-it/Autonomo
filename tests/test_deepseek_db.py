#!/usr/bin/env python3
"""
Test de DeepSeek usando API key de la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from storage import get_storage
from agent.llm_provider import DeepSeekProvider, Message

async def test_deepseek_from_db():
    print("🧪 Test de DeepSeek con API Key de DB\n")
    
    # Obtener storage
    storage = get_storage()
    
    # Obtener API key de DeepSeek
    print("1️⃣ Buscando API key de DeepSeek en DB...")
    api_key = storage.get_api_key("deepseek")
    
    if not api_key:
        print("   ❌ No hay API key de DeepSeek en la base de datos\n")
        print("   Para agregar una:")
        print("   1. Click en 🔑 en el frontend")
        print("   2. Ingresa tu DeepSeek API key")
        print("   3. Click 'Guardar'\n")
        return
    
    print(f"   ✅ API key encontrada: {api_key[:10]}...{api_key[-4:]}\n")
    
    try:
        print("2️⃣ Creando provider DeepSeek...")
        provider = DeepSeekProvider(
            model="deepseek-chat",
            api_key=api_key
        )
        print("   ✅ Provider creado\n")
        
        print("3️⃣ Enviando mensaje: 'hola como estas?'...")
        
        messages = [
            Message(role="user", content="hola como estas?")
        ]
        
        response = await provider.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        print("   ✅ Respuesta recibida!\n")
        print("4️⃣ Respuesta de DeepSeek:")
        print(f"   {response.content}\n")
        
        if response.usage:
            print(f"5️⃣ Tokens usados:")
            print(f"   - Prompt: {response.usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion: {response.usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total: {response.usage.get('total_tokens', 'N/A')}\n")
        
        print("✅ Test exitoso! DeepSeek funciona correctamente con tu API key.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nTipo de error: {type(e).__name__}")
        
        error_msg = str(e).lower()
        if 'auth' in error_msg or '401' in error_msg:
            print("\n⚠️  La API key parece ser inválida o expirada.")
            print("   Verifica tu API key en: https://platform.deepseek.com/")
        elif 'rate' in error_msg or '429' in error_msg:
            print("\n⚠️  Límite de rate alcanzado. Espera un momento.")
        else:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek_from_db())
