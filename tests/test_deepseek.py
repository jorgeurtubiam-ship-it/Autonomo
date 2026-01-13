#!/usr/bin/env python3
"""
Test simple de DeepSeek
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from agent.llm_provider import DeepSeekProvider

async def test_deepseek():
    print("🧪 Test de DeepSeek\n")
    
    # Pedir API key
    api_key = input("Ingresa tu DeepSeek API key (o 'skip' para saltar): ").strip()
    
    if api_key.lower() == 'skip':
        print("⏭️  Test saltado - sin API key")
        return
    
    try:
        print("\n1️⃣ Creando provider DeepSeek...")
        provider = DeepSeekProvider(
            model="deepseek-chat",
            api_key=api_key
        )
        print("   ✅ Provider creado\n")
        
        print("2️⃣ Enviando mensaje: 'hola como estas?'...")
        
        from agent.llm_provider import Message
        messages = [
            Message(role="user", content="hola como estas?")
        ]
        
        response = await provider.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        print("   ✅ Respuesta recibida!\n")
        print("3️⃣ Respuesta de DeepSeek:")
        print(f"   {response.content}\n")
        
        if response.usage:
            print(f"4️⃣ Tokens usados:")
            print(f"   - Prompt: {response.usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion: {response.usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total: {response.usage.get('total_tokens', 'N/A')}\n")
        
        print("✅ Test exitoso! DeepSeek funciona correctamente.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nTipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek())
