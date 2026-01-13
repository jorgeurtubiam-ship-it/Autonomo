"""
Agent Core - Motor principal del agente autónomo
Implementa el ciclo Plan & Act
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
from dataclasses import dataclass

import re
import json
import uuid
import asyncio # Added by user instruction
import os # Added by user instruction
from .llm_provider import LLMProvider, Message, LLMResponse, ToolCall
from .context import ContextManager
from .prompts import get_system_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuración del agente"""
    autonomy_level: str = "semi"  # full, semi, supervised
    max_iterations: int = 10  # Máximo de iteraciones del ciclo Plan & Act
    require_approval_for: List[str] = None  # Tools que requieren aprobación
    llm_provider: str = "ollama"
    model: str = "llama3.2:latest"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.require_approval_for is None:
            self.require_approval_for = [
                "terminate_instance",
                "delete_resource",
                "delete_file",
                "execute_command"
            ]


class ToolRegistry:
    """Registro de tools disponibles"""
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
    
    def register(self, tool):
        """Registra un tool"""
        self.tools[tool.name] = tool
        logger.info(f"Tool registrado: {tool.name}")
    
    def get(self, name: str):
        """Obtiene un tool por nombre"""
        return self.tools.get(name)
    
    def get_all_definitions(self) -> List[Dict]:
        """Obtiene definiciones de todos los tools para el LLM"""
        return [tool.get_definition() for tool in self.tools.values()]
    
    def list_tools(self) -> List[str]:
        """Lista nombres de todos los tools"""
        return list(self.tools.keys())


class AgentCore:
    """
    Motor principal del agente autónomo
    Implementa el ciclo Plan & Act
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        config: Optional[AgentConfig] = None
    ):
        """
        Args:
            llm_provider: Proveedor de LLM
            config: Configuración del agente
        """
        self.llm = llm_provider
        self.config = config or AgentConfig()
        self.context_manager = ContextManager()
        self.tool_registry = ToolRegistry()
        self.system_prompt = get_system_prompt()
        
        # Estado para aprobaciones pendientes
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"AgentCore inicializado con {llm_provider.__class__.__name__}")
    
    def reconfigure_llm(
        self,
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """Reconfigura el proveedor de LLM"""
        from .llm_provider import create_llm_provider
        
        self.llm = create_llm_provider(
            provider,
            model=model,
            api_key=api_key
        )
        self.config.llm_provider = provider
        if model:
            self.config.model = model
            
        logger.info(f"AgentCore reconfigurado con {provider} ({model})")

    async def process_message(
        self,
        user_message: str,
        conversation_id: str,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Procesa un mensaje del usuario
        
        Args:
            user_message: Mensaje del usuario
            conversation_id: ID de la conversación
            stream: Si hacer streaming de la respuesta
        
        Yields:
            Eventos del procesamiento (thinking, tool_call, message, etc.)
        """
        # Establecer conversación actual
        self.context_manager.set_current_conversation(conversation_id)
        
        # Agregar mensaje del usuario al contexto
        self.context_manager.add_message("user", user_message, conversation_id)
        
        # Iniciar ciclo Plan & Act
        iteration = 0
        
        while iteration < self.config.max_iterations:
            iteration += 1
            
            # Obtener contexto para el LLM
            messages = self._prepare_messages_for_llm(conversation_id)
            
            # Obtener definiciones de tools
            tools = self._get_tools_for_llm()
            
            # Yield evento de "thinking"
            yield {
                "type": "thinking",
                "iteration": iteration,
                "message": "Analizando y planificando..."
            }
            
            # Llamar al LLM
            try:
                logger.debug(f"LLM Request Messages: {json.dumps([{'role': m.role, 'content': m.content} for m in messages], indent=2)}")
                response = await self.llm.chat(
                    messages=messages,
                    tools=tools,
                    temperature=0.7,
                    max_tokens=4000
                )
            except Exception as e:
                logger.error(f"Error en llamada al LLM: {str(e)}", exc_info=True)
                yield {
                    "type": "error",
                    "error": str(e),
                    "message": "Error al comunicarse con el LLM"
                }
                break
            
            # Intentar extraer tool calls si no vienen nativos
            if response.content:
                parsed_tool_calls, matched_strings = self._extract_tool_calls_from_content(response.content, return_strings=True)
                if parsed_tool_calls:
                    logger.info(f"Fallback: Detectados {len(parsed_tool_calls)} tool calls en el contenido")
                    response.tool_calls = (response.tool_calls or []) + parsed_tool_calls
                    
                    # Limpiar el contenido: eliminar los bloques JSON detectados exactamente
                    clean_content = response.content
                    for s in matched_strings:
                        clean_content = clean_content.replace(s, '')
                    
                    # Eliminar puntos y coma o texto residual grueso que a veces queda entre o al final de los JSONs
                    clean_content = re.sub(r'[\s;]+', ' ', clean_content)
                    
                    response.content = clean_content.strip()
            
            # Detectar y filtrar alucinaciones si hay tool_calls
            if response.tool_calls and response.content:
                # Si el contenido tiene texto antes de los tools, suele ser el razonamiento
                reasoning = response.content.strip()
                
                # Buscar tags <thought>
                thought_match = re.search(r'<thought>(.*?)</thought>', reasoning, re.DOTALL | re.IGNORECASE)
                if thought_match:
                    reasoning = thought_match.group(1).strip()
                
                if reasoning:
                    yield {
                        "type": "thinking",
                        "message": "Analizando...",
                        "content": reasoning
                    }
                
                if self._is_hallucinated_result(response.content):
                    logger.warning("Alucinación detectada en el contenido del LLM. Filtrando...")
                    response.content = ""
            
            # Si el LLM quiere usar tools
            if response.tool_calls:
                # Procesar tool calls
                async for event in self._process_tool_calls(
                    response.tool_calls,
                    conversation_id
                ):
                    yield event
                
                # Continuar el ciclo para que el LLM procese los resultados
                continue
            
            # Si no hay tool calls, el LLM ha terminado
            if response.content:
                # Agregar respuesta al contexto
                self.context_manager.add_message(
                    "assistant",
                    response.content,
                    conversation_id
                )
                
                # Yield mensaje final
                yield {
                    "type": "message",
                    "content": response.content,
                    "finish_reason": response.finish_reason
                }
            
            # Terminar ciclo
            break
        
        # Yield evento de finalización
        yield {
            "type": "done",
            "iterations": iteration
        }

    async def process_approval(
        self,
        conversation_id: str,
        approved: bool
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Procesa la respuesta del usuario a una solicitud de aprobación
        
        Args:
            conversation_id: ID de la conversación
            approved: True si se aprobó, False si se rechazó
        
        Yields:
            Eventos de ejecución y continuación
        """
        pending = self.pending_approvals.pop(conversation_id, None)
        if not pending:
            yield {"type": "error", "message": "No hay acciones pendientes de aprobación"}
            return

        tool_call = pending["tool_call"]
        
        if approved:
            # Ejecutar el tool que estaba pausado
            logger.info(f"Aprobado: Ejecutando {tool_call.name}")
            
            # Reutilizamos la lógica de ejecución (pero solo para este tool)
            try:
                tool = self.tool_registry.get(tool_call.name)
                if not tool:
                    result = {"success": False, "error": f"Tool '{tool_call.name}' no encontrado"}
                else:
                    result = await tool.execute(**tool_call.arguments)
                
                # Yield resultado
                yield {
                    "type": "tool_result",
                    "tool": tool_call.name,
                    "tool_call_id": tool_call.id,
                    "result": result,
                    "success": result.get("success", True) if isinstance(result, dict) else True
                }
                
                # Guardar resultado en el contexto
                self.context_manager.add_message(
                    "tool",
                    str(result),
                    conversation_id,
                    tool_call_id=tool_call.id
                )
                
                # Continuar el ciclo normal (pedir al LLM que procese el resultado)
                # Llamamos a process_message pasándole un mensaje vacío o indicando que continúe
                async for event in self.process_message("", conversation_id):
                    yield event
                    
            except Exception as e:
                logger.error(f"Error ejecutando tool aprobado: {e}")
                yield {"type": "error", "error": str(e)}
        else:
            # Rechazado por el usuario
            logger.info(f"Rechazado: {tool_call.name}")
            
            result = "Error: El usuario rechazó la ejecución de esta herramienta por razones de seguridad."
            
            yield {
                "type": "tool_result",
                "tool": tool_call.name,
                "tool_call_id": tool_call.id,
                "result": result,
                "success": False
            }
            
            # Informar al contexto del rechazo
            self.context_manager.add_message(
                "tool",
                result,
                conversation_id,
                tool_call_id=tool_call.id
            )
            
            # Continuar para que el LLM sepa que fue rechazado
            async for event in self.process_message("", conversation_id):
                yield event
    
    async def _process_tool_calls(
        self,
        tool_calls: List[ToolCall],
        conversation_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Procesa llamadas a tools
        
        Args:
            tool_calls: Lista de tool calls del LLM
            conversation_id: ID de la conversación
        
        Yields:
            Eventos de ejecución de tools
        """
        # Agregar tool calls al contexto
        self.context_manager.add_message(
            "assistant",
            "",
            conversation_id,
            tool_calls=[
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments
                    }
                }
                for tc in tool_calls
            ]
        )
        
        # Ejecutar cada tool
        for tool_call in tool_calls:
            # Yield evento de tool call
            yield {
                "type": "tool_call",
                "tool": tool_call.name,
                "arguments": tool_call.arguments,
                "tool_call_id": tool_call.id
            }
            
            # Feedback visual para tools de visión (que pueden tardar)
            if tool_call.name in ["get_visual_context", "point_to_object"]:
                yield {
                    "type": "thinking",
                    "message": "Analizando imagen de la cámara móvil..." if tool_call.name == "get_visual_context" else "Señalando objeto en la pantalla...",
                    "content": ""
                }
            
            # Verificar si requiere aprobación
            if self._requires_approval(tool_call.name):
                # Guardar el tool call para ejecución posterior
                self.pending_approvals[conversation_id] = {
                    "tool_call": tool_call,
                    "timestamp": uuid.uuid4().hex # ID único para esta aprobación
                }
                
                yield {
                    "type": "approval_required",
                    "tool": tool_call.name,
                    "arguments": tool_call.arguments,
                    "tool_call_id": tool_call.id,
                    "message": f"⚠️ El tool '{tool_call.name}' requiere tu aprobación antes de ejecutarse."
                }
                # Detenemos la ejecución de este tool y del ciclo actual
                return 
            
            # Ejecutar tool
            try:
                result = await self._execute_tool(tool_call)
                
                # Agregar resultado al contexto
                self.context_manager.add_message(
                    "tool",
                    str(result),
                    conversation_id,
                    tool_call_id=tool_call.id
                )
                
                # Yield resultado
                yield {
                    "type": "tool_result",
                    "tool": tool_call.name,
                    "tool_call_id": tool_call.id,
                    "result": result,
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error ejecutando tool {tool_call.name}: {e}")
                
                error_message = f"Error: {str(e)}"
                
                # Agregar error al contexto
                self.context_manager.add_message(
                    "tool",
                    error_message,
                    conversation_id,
                    tool_call_id=tool_call.id
                )
                
                # Yield error
                yield {
                    "type": "tool_result",
                    "tool": tool_call.name,
                    "tool_call_id": tool_call.id,
                    "error": str(e),
                    "success": False
                }
    
    async def _execute_tool(self, tool_call: ToolCall) -> Any:
        """
        Ejecuta un tool
        
        Args:
            tool_call: Tool call a ejecutar
        
        Returns:
            Resultado del tool
        """
        tool = self.tool_registry.get(tool_call.name)
        
        if not tool:
            raise ValueError(f"Tool no encontrado: {tool_call.name}")
        
        logger.info(f"Ejecutando tool: {tool_call.name} con args: {tool_call.arguments}")
        
        # Ejecutar tool
        result = await tool.execute(**tool_call.arguments)
        
        return result
    
    def _extract_tool_calls_from_content(self, content: str, return_strings: bool = False) -> Any:
        """
        Intenta extraer tool calls de un texto JSON (fallback para modelos que no usan el campo nativo)
        """
        tool_calls = []
        matched_strings = []
        
        # 1. Intentar encontrar bloques balanceados { ... }
        potential_blocks = []
        brace_start_indices = [m.start() for m in re.finditer(r'\{', content)]
        last_end = -1
        
        for start in brace_start_indices:
            if start < last_end:
                continue
                
            # Solo procesar si el bloque parece empezar un "name" de tool
            snippet = content[start:start+100]
            if not ('"name"' in snippet or "'name'" in snippet):
                continue
                
            # Buscar el cierre balanceado
            depth = 0
            for i in range(start, len(content)):
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0:
                        block = content[start:i+1]
                        potential_blocks.append(block)
                        last_end = i + 1
                        break
        
        # Procesar bloques encontrados
        processed_start_indices = set()
        for block in potential_blocks:
            try:
                data = self._fuzzy_json_parse(block)
                if data and isinstance(data, dict) and "name" in data:
                    name = data["name"]
                    args = data.get("arguments") or data.get("parameters") or {}
                    
                    tool_calls.append(ToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        name=name,
                        arguments=args
                    ))
                    matched_strings.append(block)
            except Exception:
                continue
                
        if return_strings:
            return tool_calls, matched_strings
        return tool_calls
    
    def _is_hallucinated_result(self, content: str) -> bool:
        """
        Detecta si el contenido parece ser un resultado alucinado (predicho) por el modelo.
        Suele ocurrir con modelos pequeños que imitan el output esperado.
        """
        if not content:
            return False
            
        content_lower = content.lower()
        
        # Patrones comunes de alucinación de resultados (solo si son JSON puros muy sospechosos)
        hallucination_indicators = [
            '"instances": [',
            '"reservations": [',
        ]
        
        # Si contiene JSON y parece un resultado de herramienta
        if content.strip().startswith('{') and any(ind in content_lower for ind in hallucination_indicators):
            return True
            
        # Si parece una simulación de respuesta
        if "asistente:" in content_lower or "agente:" in content_lower or "usuario:" in content_lower:
            # A veces el modelo alucina toda la conversación
            if any(ind in content_lower for ind in hallucination_indicators):
                return True
                
        return False

    def _fuzzy_json_parse(self, s: str) -> Optional[Dict]:
        """
        Intenta parsear JSON de forma flexible para corregir errores comunes de LLMs pequeños
        """
        try:
            return json.loads(s)
        except:
            pass
            
        try:
            # 1. Corregir ""clave" -> "clave"
            fixed = re.sub(r'""([^"]+)":', r'"\1":', s)
            # 2. Corregir 'clave': -> "clave":
            fixed = re.sub(r"'([^']+)'\s*:", r'"\1":', fixed)
            # 3. Corregir : 'valor' -> : "valor"
            fixed = re.sub(r':\s*\'([^\']*)\'', r': "\1"', fixed)
            # 4. Eliminar comas finales antes de } o ]
            fixed = re.sub(r',\s*([\]\}])', r'\1', fixed)
            
            return json.loads(fixed)
        except:
            return None

    def _prepare_messages_for_llm(self, conversation_id: str) -> List[Message]:
        """
        Prepara mensajes para el LLM
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            Lista de mensajes formateados
        """
        # Obtener mensajes del contexto
        system_prompt = self.system_prompt
        
        # Inyectar memoria visual si hay snapshots recientes
        from agent.vision_manager import vision_manager
        status = vision_manager.get_status()
        if status.get("active") and status.get("last_snapshot"):
            visual_context = f"\n\n## Estado Visual Actual (Cámara Móvil)\n- ESTADO: **ACTIVA**\n- ÚLTIMO SNAPSHOT: {status['last_snapshot']}\n- Estás viendo a través del móvil del usuario.\n- SI EL USUARIO TE PREGUNTA POR ALGO QUE 'VES' O SU ENTORNO: Debes usar la herramienta `get_visual_context` inmediatamente para obtener la descripción actual."
            system_prompt += visual_context
        else:
            system_prompt += "\n\n## Estado Visual\n- Cámara Móvil: Inactiva o sin señal. Si el usuario te pide ver algo, indícale que debe activar la visión con el botón del sidebar."

        context_messages = self.context_manager.get_context_for_llm(
            conversation_id,
            system_prompt=system_prompt
        )
        
        # Convertir a formato Message
        messages = []
        for msg in context_messages:
            messages.append(Message(
                role=msg["role"],
                content=msg["content"],
                tool_calls=msg.get("tool_calls"),
                tool_call_id=msg.get("tool_call_id")
            ))
        
        return messages
    
    def _get_tools_for_llm(self) -> List[Dict]:
        """
        Obtiene definiciones de tools para el LLM
        
        Returns:
            Lista de definiciones de tools
        """
        tool_definitions = self.tool_registry.get_all_definitions()
        
        # Convertir a formato esperado por el LLM (OpenAI format)
        formatted_tools = []
        for tool_def in tool_definitions:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool_def["name"],
                    "description": tool_def["description"],
                    "parameters": tool_def["parameters"]
                }
            })
        
        return formatted_tools
    
    def _requires_approval(self, tool_name: str) -> bool:
        """
        Verifica si un tool requiere aprobación
        
        Args:
            tool_name: Nombre del tool
        
        Returns:
            True si requiere aprobación
        """
        if self.config.autonomy_level == "full":
            return False
        elif self.config.autonomy_level == "supervised":
            return True
        else: # semi
            return tool_name in self.config.require_approval_for
    def register_tool(self, tool):
        """
        Registra un tool en el agente
        
        Args:
            tool: Tool a registrar
        """
        self.tool_registry.register(tool)
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Obtiene el historial de una conversación
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            Lista de mensajes
        """
        messages = self.context_manager.get_messages(conversation_id)
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    
    def reconfigure_llm(
        self,
        provider: str,
        model: str = None,
        api_key: str = None
    ):
        """
        Reconfigura el LLM provider en caliente
        
        Args:
            provider: Nombre del provider (ollama, openai, anthropic, deepseek)
            model: Modelo específico a usar
            api_key: API key para el provider (si es necesario)
        """
        logger.info(f"Reconfigurando LLM: {provider} con modelo {model}")
        
        try:
            # Importar providers
            from .llm_provider import OllamaProvider
            
            # Crear nuevo provider según el tipo
            if provider == "ollama":
                new_llm = OllamaProvider(
                    model=model or "llama3.2:latest"
                )
            
            elif provider == "openai":
                try:
                    from openai import AsyncOpenAI
                    if not api_key:
                        api_key = getattr(self.config, 'openai_api_key', None)
                    if not api_key:
                        raise ValueError("OpenAI API key requerida")
                    
                    # Crear wrapper para OpenAI
                    from .llm_provider import OpenAIProvider
                    new_llm = OpenAIProvider(
                        model=model or "gpt-4",
                        api_key=api_key
                    )
                except ImportError:
                    raise ValueError("Librería openai no instalada. Ejecuta: pip install openai")
            
            elif provider == "anthropic":
                try:
                    import anthropic
                    if not api_key:
                        api_key = getattr(self.config, 'anthropic_api_key', None)
                    if not api_key:
                        raise ValueError("Anthropic API key requerida")
                    
                    from .llm_provider import AnthropicProvider
                    new_llm = AnthropicProvider(
                        model=model or "claude-3-sonnet-20240229",
                        api_key=api_key
                    )
                except ImportError:
                    raise ValueError("Librería anthropic no instalada. Ejecuta: pip install anthropic")
            
            elif provider == "deepseek":
                try:
                    from openai import AsyncOpenAI
                    if not api_key:
                        api_key = getattr(self.config, 'deepseek_api_key', None)
                    if not api_key:
                        raise ValueError("DeepSeek API key requerida")
                    
                    from .llm_provider import DeepSeekProvider
                    new_llm = DeepSeekProvider(
                        model=model or "deepseek-chat",
                        api_key=api_key
                    )
                except ImportError:
                    raise ValueError("Librería openai no instalada. Ejecuta: pip install openai")
            
            else:
                raise ValueError(f"Provider no soportado: {provider}")
            
            # Reemplazar el LLM actual
            old_llm = self.llm
            self.llm = new_llm
            
            # Actualizar config
            self.config.llm_provider = provider
            if model:
                self.config.model = model
            
            logger.info(f"LLM reconfigurado exitosamente: {provider} ({model})")
            
            # Limpiar el LLM anterior si es necesario
            del old_llm
            
        except Exception as e:
            logger.error(f"Error reconfigurando LLM: {e}")
            raise
