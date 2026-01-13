#!/usr/bin/env python3
"""
Test automático de DeepSeek con API key de prueba
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from agent.llm_provider import DeepSeekProvider, Message

async def test_deepseek_auto():
    print("🧪 Test Automático de DeepSeek\n")
    
    # Usar API key de prueba (fallará pero veremos el error exacto)
    api_key = "sk-test-fake-key-for-testing"
    
    try:
        print("1️⃣ Creando provider DeepSeek...")
        provider = DeepSeekProvider(
            model="deepseek-chat",
            api_key=api_key
        )
        print("   ✅ Provider creado\n")
        
        print("2️⃣ Enviando mensaje: 'hola como estas?'...")
        
        messages = [
            Message(role="user", content="hola como estas?")
        ]
        
        response = await provider.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        print("   ✅ Respuesta recibida!\n")
        print(f"3️⃣ Respuesta: {response.content}\n")
        
    except Exception as e:
        print(f"\n❌ Error esperado (API key inválida):")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)[:200]}\n")
        
        # Verificar que el error es por API key
        error_msg = str(e).lower()
        if 'api' in error_msg or 'auth' in error_msg or 'key' in error_msg or 'invalid' in error_msg:
            print("✅ El provider funciona correctamente")
            print("   (Solo necesita una API key válida)\n")
        else:
            print("⚠️  Error inesperado - puede haber otro problema\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek_auto())
