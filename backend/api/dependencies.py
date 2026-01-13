"""
Dependencias compartidas de la API
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
import sys
import os
import json

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agent import AgentCore, AgentConfig, create_llm_provider
from tools import get_all_tools
from storage import get_storage, ConversationStorage


# Singleton del agente
_agent_instance: Optional[AgentCore] = None


def get_agent() -> AgentCore:
    """
    Dependency para obtener instancia del agente
    
    Returns:
        Instancia del AgentCore
    """
    global _agent_instance
    
    if _agent_instance is None:
        # Crear configuración
        config = AgentConfig(
            autonomy_level="semi",
            max_iterations=10
        )
        
        # Crear LLM (por defecto Ollama)
        llm = create_llm_provider(
            "ollama",
            model="llama3.2:latest"
        )
        
        # Crear agente
        _agent_instance = AgentCore(llm, config)
        
        # Registrar tools
        for tool in get_all_tools():
            _agent_instance.register_tool(tool)
    
    return _agent_instance


def get_storage_dependency() -> ConversationStorage:
    """
    Dependency para obtener instancia del storage
    
    Returns:
        Instancia del ConversationStorage
    """
    return get_storage()


def load_conversation_history(
    conversation_id: str,
    agent: AgentCore,
    storage: ConversationStorage
):
    """
    Carga el historial de una conversación en el contexto del agente
    """
    # Verificar si ya está cargado
    if conversation_id in agent.context_manager.conversations:
        return
    
    # Obtener mensajes de la base de datos
    messages = storage.get_messages(conversation_id)
    
    if not messages:
        return
    
    # Agregar mensajes al contexto
    for msg in messages:
        tool_calls = msg.tool_calls
        if isinstance(tool_calls, str):
            try:
                tool_calls = json.loads(tool_calls)
            except:
                tool_calls = None
                
        agent.context_manager.add_message(
            role=msg.role,
            content=msg.content,
            conversation_id=conversation_id,
            tool_calls=tool_calls,
            tool_call_id=msg.tool_call_id
        )


def reconfigure_agent(
    llm_provider: Optional[str] = None,
    model: Optional[str] = None,
    autonomy_level: Optional[str] = None
):
    """
    Reconfigura el agente con nuevos parámetros
    
    Args:
        llm_provider: Nuevo proveedor de LLM
        model: Nuevo modelo
        autonomy_level: Nuevo nivel de autonomía
    """
    global _agent_instance
    
    if llm_provider or model:
        # Crear nuevo LLM
        llm = create_llm_provider(
            llm_provider or "ollama",
            model=model
        )
        
        # Crear nueva configuración
        config = AgentConfig(
            autonomy_level=autonomy_level or "semi",
            max_iterations=10
        )
        
        # Recrear agente
        _agent_instance = AgentCore(llm, config)
        
        # Re-registrar tools
        for tool in get_all_tools():
            _agent_instance.register_tool(tool)
    
    elif autonomy_level:
        # Solo actualizar configuración
        if _agent_instance:
            _agent_instance.config.autonomy_level = autonomy_level
