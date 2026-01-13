"""
Context Manager
Gestiona el contexto de conversación y memoria del agente
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ConversationMessage:
    """Mensaje en la conversación"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Contexto de una conversación"""
    conversation_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    Gestiona el contexto de conversaciones y memoria del agente
    """
    
    def __init__(self, max_context_tokens: int = 8000):
        """
        Args:
            max_context_tokens: Máximo de tokens en el contexto
        """
        self.max_context_tokens = max_context_tokens
        self.conversations: Dict[str, ConversationContext] = {}
        self.current_conversation_id: Optional[str] = None
    
    def create_conversation(self, conversation_id: str) -> ConversationContext:
        """
        Crea una nueva conversación
        
        Args:
            conversation_id: ID único de la conversación
        
        Returns:
            Contexto de la conversación creada
        """
        context = ConversationContext(conversation_id=conversation_id)
        self.conversations[conversation_id] = context
        self.current_conversation_id = conversation_id
        return context
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Obtiene una conversación existente
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            Contexto de la conversación o None si no existe
        """
        return self.conversations.get(conversation_id)
    
    def set_current_conversation(self, conversation_id: str):
        """
        Establece la conversación actual
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id not in self.conversations:
            self.create_conversation(conversation_id)
        self.current_conversation_id = conversation_id
    
    def add_message(
        self,
        role: str,
        content: str,
        conversation_id: Optional[str] = None,
        tool_calls: Optional[List[Dict]] = None,
        tool_call_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """
        Agrega un mensaje a la conversación
        
        Args:
            role: Rol del mensaje ("user", "assistant", "system", "tool")
            content: Contenido del mensaje
            conversation_id: ID de la conversación (usa actual si no se especifica)
            tool_calls: Llamadas a tools (si las hay)
            tool_call_id: ID de tool call (para mensajes de tool)
            metadata: Metadata adicional
        
        Returns:
            Mensaje creado
        """
        conv_id = conversation_id or self.current_conversation_id
        
        if not conv_id:
            raise ValueError("No hay conversación activa")
        
        if conv_id not in self.conversations:
            self.create_conversation(conv_id)
        
        message = ConversationMessage(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            metadata=metadata or {}
        )
        
        context = self.conversations[conv_id]
        context.messages.append(message)
        context.updated_at = datetime.now()
        
        return message
    
    def get_messages(
        self,
        conversation_id: Optional[str] = None,
        limit: Optional[int] = None,
        include_system: bool = True
    ) -> List[ConversationMessage]:
        """
        Obtiene mensajes de una conversación
        
        Args:
            conversation_id: ID de la conversación (usa actual si no se especifica)
            limit: Límite de mensajes a retornar (más recientes)
            include_system: Si incluir mensajes del sistema
        
        Returns:
            Lista de mensajes
        """
        conv_id = conversation_id or self.current_conversation_id
        
        if not conv_id or conv_id not in self.conversations:
            return []
        
        messages = self.conversations[conv_id].messages
        
        if not include_system:
            messages = [m for m in messages if m.role != "system"]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_for_llm(
        self,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el contexto formateado para el LLM
        
        Args:
            conversation_id: ID de la conversación
            system_prompt: System prompt a incluir
        
        Returns:
            Lista de mensajes formateados para el LLM
        """
        messages = []
        
        # Agregar system prompt si se proporciona
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Obtener mensajes de la conversación
        conv_messages = self.get_messages(conversation_id)
        
        # Convertir a formato para LLM
        for msg in conv_messages:
            formatted_msg = {
                "role": msg.role,
                "content": msg.content
            }
            
            if msg.tool_calls:
                formatted_msg["tool_calls"] = msg.tool_calls
            
            if msg.tool_call_id:
                formatted_msg["tool_call_id"] = msg.tool_call_id
            
            messages.append(formatted_msg)
        
        # Truncar si excede el límite de tokens
        # TODO: Implementar truncamiento inteligente basado en tokens
        return messages
    
    def clear_conversation(self, conversation_id: Optional[str] = None):
        """
        Limpia los mensajes de una conversación
        
        Args:
            conversation_id: ID de la conversación (usa actual si no se especifica)
        """
        conv_id = conversation_id or self.current_conversation_id
        
        if conv_id and conv_id in self.conversations:
            self.conversations[conv_id].messages = []
            self.conversations[conv_id].updated_at = datetime.now()
    
    def delete_conversation(self, conversation_id: str):
        """
        Elimina una conversación completamente
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de la conversación
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            Resumen con estadísticas
        """
        context = self.get_conversation(conversation_id)
        
        if not context:
            return {}
        
        user_messages = [m for m in context.messages if m.role == "user"]
        assistant_messages = [m for m in context.messages if m.role == "assistant"]
        tool_messages = [m for m in context.messages if m.role == "tool"]
        
        return {
            "conversation_id": conversation_id,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "total_messages": len(context.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "tool_executions": len(tool_messages),
            "metadata": context.metadata
        }
    
    def export_conversation(self, conversation_id: str) -> str:
        """
        Exporta una conversación a JSON
        
        Args:
            conversation_id: ID de la conversación
        
        Returns:
            JSON string de la conversación
        """
        context = self.get_conversation(conversation_id)
        
        if not context:
            return "{}"
        
        data = {
            "conversation_id": context.conversation_id,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "tool_calls": m.tool_calls,
                    "tool_call_id": m.tool_call_id,
                    "metadata": m.metadata
                }
                for m in context.messages
            ],
            "metadata": context.metadata
        }
        
        return json.dumps(data, indent=2)
    
    def import_conversation(self, json_data: str) -> ConversationContext:
        """
        Importa una conversación desde JSON
        
        Args:
            json_data: JSON string de la conversación
        
        Returns:
            Contexto de la conversación importada
        """
        data = json.loads(json_data)
        
        context = ConversationContext(
            conversation_id=data["conversation_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )
        
        for msg_data in data["messages"]:
            message = ConversationMessage(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                tool_calls=msg_data.get("tool_calls"),
                tool_call_id=msg_data.get("tool_call_id"),
                metadata=msg_data.get("metadata", {})
            )
            context.messages.append(message)
        
        self.conversations[context.conversation_id] = context
        
        return context
