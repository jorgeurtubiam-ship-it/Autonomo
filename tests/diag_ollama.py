import asyncio
import sys
import os
import json
import aiohttp

# Configurar path para importar desde backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.llm_provider import OllamaProvider, Message

async def test_ollama_tools():
    print("Testing Ollama with tools...")
    provider = OllamaProvider(model="llama3.2:latest")
    
    from agent.prompts import get_system_prompt
    
    messages = [
        Message(role="system", content=get_system_prompt()),
        Message(role="user", content="Lista los archivos del directorio actual")
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Ejecuta un comando en la terminal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Comando a ejecutar"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]
    
    try:
        response = await provider.chat(messages, tools=tools)
        print(f"Content: {response.content}")
        if response.tool_calls:
            print(f"Tool Calls: {response.tool_calls}")
        else:
            print("No tool calls triggered.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama_tools())
