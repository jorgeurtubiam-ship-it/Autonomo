"""
Tools Routes - Endpoints para gestionar tools
"""

from fastapi import APIRouter, Depends
from typing import List

from ..models import ToolsList, ToolInfo
from ..dependencies import get_agent
from agent import AgentCore

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("/", response_model=ToolsList)
async def list_tools(agent: AgentCore = Depends(get_agent)):
    """
    Lista todos los tools disponibles
    
    Retorna información de cada tool incluyendo:
    - Nombre
    - Descripción
    - Categoría
    - Parámetros
    """
    tools_list = agent.tool_registry.list_tools()
    tools_info = []
    
    for tool_name in tools_list:
        tool = agent.tool_registry.get(tool_name)
        definition = tool.get_definition()
        
        tools_info.append(ToolInfo(
            name=definition["name"],
            description=definition["description"],
            category=getattr(tool, "category", "general"),
            parameters=definition["parameters"]
        ))
    
    return ToolsList(
        tools=tools_info,
        total=len(tools_info)
    )


@router.get("/{tool_name}")
async def get_tool_info(
    tool_name: str,
    agent: AgentCore = Depends(get_agent)
):
    """
    Obtiene información detallada de un tool específico
    
    - **tool_name**: Nombre del tool
    """
    tool = agent.tool_registry.get(tool_name)
    
    if not tool:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' no encontrado"
        )
    
    definition = tool.get_definition()
    
    return {
        "name": definition["name"],
        "description": definition["description"],
        "category": getattr(tool, "category", "general"),
        "parameters": definition["parameters"]
    }
