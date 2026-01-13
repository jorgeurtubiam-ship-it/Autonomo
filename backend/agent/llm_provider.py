"""
LLM Provider Abstraction
Soporta múltiples proveedores: OpenAI, Anthropic, Ollama
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import json
import logging

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

try:
    import aiohttp
except ImportError:
    aiohttp = None


@dataclass
class Message:
    """Mensaje en la conversación"""
    role: str  # "user", "assistant", "system"
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


@dataclass
class ToolCall:
    """Llamada a un tool"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Respuesta del LLM"""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str = "stop"
    usage: Optional[Dict[str, int]] = None


class LLMProvider(ABC):
    """Clase base para proveedores de LLM"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> LLMResponse:
        """Envía mensajes al LLM y obtiene respuesta"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Streaming de respuesta del LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """Proveedor OpenAI (GPT-4, GPT-3.5, etc.)"""
    
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        if not AsyncOpenAI:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def _format_messages(self, messages: List[Message]) -> List[Dict]:
        """Convierte mensajes al formato de OpenAI"""
        formatted = []
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}
            
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
                formatted_msg["role"] = "tool"
            
            formatted.append(formatted_msg)
        
        return formatted
    
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> LLMResponse:
        """Llamada a OpenAI API"""
        
        formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = await self.client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        
        # Extraer tool calls si existen
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in message.tool_calls
            ]
        
        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
    
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Streaming de respuesta"""
        
        formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        stream = await self.client.chat.completions.create(**kwargs)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicProvider(LLMProvider):
    """Proveedor Anthropic (Claude)"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        if not AsyncAnthropic:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.client = AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    
    def _format_messages(self, messages: List[Message]) -> tuple:
        """Convierte mensajes al formato de Anthropic"""
        system_message = None
        formatted = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                formatted.append({"role": msg.role, "content": msg.content})
        
        return system_message, formatted
    
    def _convert_tools_to_anthropic(self, tools: List[Dict]) -> List[Dict]:
        """Convierte tools de formato OpenAI a Anthropic"""
        anthropic_tools = []
        for tool in tools:
            anthropic_tools.append({
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"]
            })
        return anthropic_tools
    
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> LLMResponse:
        """Llamada a Anthropic API"""
        
        system_message, formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic(tools)
        
        response = await self.client.messages.create(**kwargs)
        
        # Extraer contenido y tool calls
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    )
                )
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        )
    
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Streaming de respuesta"""
        
        system_message, formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_message:
            kwargs["system"] = system_message
        
        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic(tools)
        
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text


class DeepSeekProvider(LLMProvider):
    """Proveedor DeepSeek (API directa)"""
    
    def __init__(self, model: str = "deepseek-chat", api_key: Optional[str] = None, **kwargs):
        super().__init__(model, api_key, **kwargs)
        if not AsyncOpenAI:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        # DeepSeek usa API compatible con OpenAI
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
    
    def _format_messages(self, messages: List[Message]) -> List[Dict]:
        """Convierte mensajes al formato de DeepSeek"""
        formatted = []
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content}
            
            if msg.tool_calls:
                # DeepSeek no soporta tool_calls en el mismo formato que OpenAI
                # Si hay tool_calls, los convertimos a texto en el content
                tool_desc = "\n\nTool calls realizados:\n"
                for tc in msg.tool_calls:
                    # Notar que tc es un dict que puede tener 'function' (format OpenAI)
                    name = tc.get('name')
                    args = tc.get('arguments', {})
                    
                    if not name and 'function' in tc:
                        name = tc['function'].get('name', 'unknown')
                        args = tc['function'].get('arguments', {})
                    
                    tool_desc += f"- {name}: {args}\n"
                formatted_msg["content"] = (msg.content or "") + tool_desc
            
            if msg.tool_call_id:
                # Convertir mensaje de tool a mensaje de assistant (DeepSeek workaround)
                formatted_msg["role"] = "assistant"
                formatted_msg["content"] = f"Tool result ({msg.tool_call_id}): {msg.content}"
            
            formatted.append(formatted_msg)
        
        return formatted
    
    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> LLMResponse:
        """Llamada a DeepSeek API"""
        
        formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = await self.client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        
        # Extraer tool calls si existen
        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                )
                for tc in message.tool_calls
            ]
        
        return LLMResponse(
            content=message.content or "",
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
    
    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Streaming de respuesta"""
        
        formatted_messages = self._format_messages(messages)
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        stream = await self.client.chat.completions.create(**kwargs)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class OllamaProvider(LLMProvider):
    """Proveedor Ollama (modelos locales)"""
    
    def __init__(self, model: str = "deepseek-coder:33b", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model, None, **kwargs)
        self.base_url = base_url
        if not aiohttp:
            raise ImportError("aiohttp package not installed. Run: pip install aiohttp")
    
    def _format_messages(self, messages: List[Message]) -> List[Dict]:
        """Convierte mensajes al formato de Ollama/OpenAI"""
        formatted = []
        for msg in messages:
            formatted_msg = {"role": msg.role, "content": msg.content or ""}
            
            if msg.tool_calls:
                tool_calls = msg.tool_calls
                if isinstance(tool_calls, str):
                    try:
                        tool_calls = json.loads(tool_calls)
                    except:
                        tool_calls = []
                formatted_msg["tool_calls"] = tool_calls
            
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
            
            formatted.append(formatted_msg)
        
        return formatted

    async def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False
    ) -> LLMResponse:
        """Llamada a Ollama API"""
        
        formatted_messages = self._format_messages(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if tools:
            payload["tools"] = tools
        
        # DEBUG: Log the request payload
        logger.debug(f"Ollama Request Payload: {json.dumps(payload)}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API Error ({response.status}): {error_text}")
                    
                result = await response.json()
                logger.debug(f"Ollama Response: {json.dumps(result)}")
                
                # Extraer tool calls si existen
                tool_calls = None
                message = result.get("message", {})
                
                if "tool_calls" in message and message["tool_calls"]:
                    tool_calls = []
                    for i, tc in enumerate(message["tool_calls"]):
                        args = tc["function"]["arguments"]
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                logger.error(f"Error parsing tool arguments: {args}")
                                args = {"raw_arguments": args}
                        
                        tool_calls.append(ToolCall(
                            id=tc.get("id", f"call_{i}"),
                            name=tc["function"]["name"],
                            arguments=args
                        ))
                
                return LLMResponse(
                    content=message.get("content", ""),
                    tool_calls=tool_calls,
                    finish_reason="stop"
                )

    async def chat_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> AsyncGenerator[str, None]:
        """Streaming de respuesta"""
        
        formatted_messages = self._format_messages(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if tools:
            payload["tools"] = tools
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    yield f"Error: {error_text}"
                    return

                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            message = data.get("message", {})
                            
                            # Ceder contenido de texto
                            if "content" in message:
                                content = message["content"]
                                if content:
                                    yield content
                            
                            # Si hay tool_calls, podríamos ceder una señal o simplemente
                            # dejar que el llamador lo maneje. Dado que chat_stream solo 
                            # devuelve str (content), si hay tool_calls avisamos por log
                            if "tool_calls" in message and message["tool_calls"]:
                                logger.info(f"Detectados tool_calls en stream de Ollama: {message['tool_calls']}")
                        except Exception:
                            continue

def create_llm_provider(
    provider_type: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> LLMProvider:
    """
    Factory para crear proveedor de LLM
    
    Args:
        provider_type: "openai", "anthropic", "deepseek", "ollama"
        model: Nombre del modelo (opcional, usa default)
        api_key: API key (opcional, usa env var)
        **kwargs: Argumentos adicionales
    
    Returns:
        Instancia de LLMProvider
    """
    
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "deepseek": DeepSeekProvider,
        "ollama": OllamaProvider
    }
    
    if provider_type not in providers:
        raise ValueError(f"Provider no soportado: {provider_type}. Opciones: {list(providers.keys())}")
    
    provider_class = providers[provider_type]
    
    # Ollama no usa api_key
    if provider_type == "ollama":
        if model:
            return provider_class(model=model, **kwargs)
        else:
            return provider_class(**kwargs)
    else:
        if model:
            return provider_class(model=model, api_key=api_key, **kwargs)
        else:
            return provider_class(api_key=api_key, **kwargs)
