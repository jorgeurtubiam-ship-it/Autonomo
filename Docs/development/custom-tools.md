# Crear Tools Personalizados

Guía para extender el agente con tus propios tools.

## Estructura de un Tool

```python
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class MyToolParams(BaseModel):
    """Parámetros del tool"""
    param1: str = Field(description="Descripción del parámetro")
    param2: Optional[int] = Field(default=None, description="Parámetro opcional")

class MyTool:
    """Tool personalizado"""
    
    name = "my_tool"
    description = "Descripción de qué hace el tool"
    
    async def execute(self, params: MyToolParams) -> Dict[str, Any]:
        """
        Ejecuta el tool.
        
        Args:
            params: Parámetros validados
            
        Returns:
            Resultado de la ejecución
        """
        # Tu lógica aquí
        result = f"Procesando {params.param1}"
        
        return {
            "success": True,
            "result": result
        }
    
    def get_definition(self) -> Dict[str, Any]:
        """
        Retorna definición del tool para el LLM.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Descripción del parámetro"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Parámetro opcional"
                    }
                },
                "required": ["param1"]
            }
        }
```

## Ejemplo Completo: Tool de Slack

```python
# backend/tools/custom/slack_tool.py

from typing import Dict, Any
from pydantic import BaseModel, Field
import aiohttp

class SlackMessageParams(BaseModel):
    channel: str = Field(description="Canal de Slack (#general, #alerts, etc.)")
    message: str = Field(description="Mensaje a enviar")
    username: str = Field(default="Agente", description="Nombre del bot")

class SlackTool:
    """Tool para enviar mensajes a Slack"""
    
    name = "send_slack_message"
    description = "Envía un mensaje a un canal de Slack"
    category = "notifications"
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def execute(self, params: SlackMessageParams) -> Dict[str, Any]:
        """Envía mensaje a Slack"""
        
        payload = {
            "channel": params.channel,
            "text": params.message,
            "username": params.username
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "message": f"Mensaje enviado a {params.channel}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Error {response.status}"
                    }
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Canal de Slack"
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensaje a enviar"
                    },
                    "username": {
                        "type": "string",
                        "description": "Nombre del bot",
                        "default": "Agente"
                    }
                },
                "required": ["channel", "message"]
            }
        }
```

## Registrar el Tool

```python
# backend/agent/tool_registry.py

from tools.custom.slack_tool import SlackTool

class ToolRegistry:
    def __init__(self, config):
        self.tools = {}
        self.config = config
        
        # Registrar tools
        self._register_default_tools()
        self._register_custom_tools()
    
    def _register_custom_tools(self):
        """Registra tools personalizados"""
        
        # Slack
        if self.config.get("slack", {}).get("enabled"):
            slack_tool = SlackTool(
                webhook_url=self.config["slack"]["webhook_url"]
            )
            self.register(slack_tool)
    
    def register(self, tool):
        """Registra un tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str):
        """Obtiene un tool por nombre"""
        return self.tools.get(name)
    
    def get_all_definitions(self):
        """Obtiene definiciones de todos los tools"""
        return [tool.get_definition() for tool in self.tools.values()]
```

## Tool con Validación Avanzada

```python
from pydantic import BaseModel, Field, validator

class DatabaseQueryParams(BaseModel):
    query: str = Field(description="Query SQL a ejecutar")
    database: str = Field(description="Nombre de la base de datos")
    
    @validator('query')
    def validate_query(cls, v):
        """Valida que la query sea segura"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE']
        if any(keyword in v.upper() for keyword in dangerous_keywords):
            raise ValueError("Query contiene operaciones peligrosas")
        return v
    
    @validator('database')
    def validate_database(cls, v):
        """Valida que la base de datos exista"""
        allowed_dbs = ['production', 'staging', 'development']
        if v not in allowed_dbs:
            raise ValueError(f"Base de datos no permitida: {v}")
        return v
```

## Tool con Manejo de Errores

```python
class RobustTool:
    async def execute(self, params):
        try:
            # Intentar operación
            result = await self._do_something(params)
            return {"success": True, "result": result}
            
        except ConnectionError as e:
            return {
                "success": False,
                "error": "Error de conexión",
                "details": str(e),
                "retry": True
            }
            
        except ValueError as e:
            return {
                "success": False,
                "error": "Parámetros inválidos",
                "details": str(e),
                "retry": False
            }
            
        except Exception as e:
            # Log error
            logger.error(f"Error inesperado: {e}")
            return {
                "success": False,
                "error": "Error interno",
                "retry": False
            }
```

## Tool con Streaming

```python
class StreamingTool:
    async def execute(self, params):
        """Tool que retorna resultados progresivamente"""
        
        async def stream_results():
            for i in range(10):
                yield {
                    "type": "progress",
                    "current": i + 1,
                    "total": 10,
                    "message": f"Procesando item {i+1}"
                }
                await asyncio.sleep(0.5)
            
            yield {
                "type": "complete",
                "result": "Proceso completado"
            }
        
        return stream_results()
```

## Tool con Cache

```python
from functools import lru_cache
import hashlib
import json

class CachedTool:
    def __init__(self):
        self.cache = {}
    
    def _get_cache_key(self, params):
        """Genera key de cache desde parámetros"""
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    async def execute(self, params):
        # Verificar cache
        cache_key = self._get_cache_key(params)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Ejecutar y cachear
        result = await self._do_expensive_operation(params)
        self.cache[cache_key] = result
        return result
```

## Testing

```python
# tests/tools/test_slack_tool.py

import pytest
from tools.custom.slack_tool import SlackTool, SlackMessageParams

@pytest.mark.asyncio
async def test_slack_tool():
    tool = SlackTool(webhook_url="https://hooks.slack.com/test")
    
    params = SlackMessageParams(
        channel="#test",
        message="Test message"
    )
    
    result = await tool.execute(params)
    
    assert result["success"] == True
    assert "enviado" in result["message"]

def test_slack_tool_definition():
    tool = SlackTool(webhook_url="test")
    definition = tool.get_definition()
    
    assert definition["name"] == "send_slack_message"
    assert "channel" in definition["parameters"]["properties"]
```

## Mejores Prácticas

1. **Validación**: Usa Pydantic para validar parámetros
2. **Documentación**: Describe claramente qué hace el tool
3. **Manejo de errores**: Retorna errores descriptivos
4. **Idempotencia**: Los tools deben ser idempotentes cuando sea posible
5. **Timeout**: Implementa timeouts para operaciones largas
6. **Logging**: Registra todas las ejecuciones
7. **Testing**: Escribe tests para cada tool

## Próximos Pasos

- [Arquitectura de Tools](../architecture/tools-system.md)
- [Testing](testing.md)
- [Contribuir](contributing.md)
