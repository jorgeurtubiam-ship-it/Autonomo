"""
Modelos de Response para la API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolCallInfo(BaseModel):
    """Información de una llamada a tool"""
    id: str
    name: str
    arguments: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response de chat"""
    conversation_id: str = Field(..., description="ID de la conversación")
    message: str = Field(..., description="Respuesta del agente")
    tool_calls: Optional[List[ToolCallInfo]] = Field(None, description="Tools ejecutados")
    iterations: int = Field(..., description="Número de iteraciones del ciclo Plan & Act")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "message": "Archivo creado exitosamente",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "name": "write_file",
                        "arguments": {"path": "hello.txt", "content": "Hola Mundo"}
                    }
                ],
                "iterations": 2
            }
        }


class ConversationInfo(BaseModel):
    """Información de una conversación"""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv_123",
                "title": "Mi conversación",
                "created_at": "2024-12-25T10:00:00",
                "updated_at": "2024-12-25T10:30:00",
                "message_count": 10
            }
        }


class ConversationList(BaseModel):
    """Lista de conversaciones"""
    conversations: List[ConversationInfo]
    total: int


class ToolInfo(BaseModel):
    """Información de un tool"""
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]


class ToolsList(BaseModel):
    """Lista de tools disponibles"""
    tools: List[ToolInfo]
    total: int


class ConfigResponse(BaseModel):
    """Configuración actual"""
    llm_provider: str
    model: str
    autonomy_level: str
    temperature: float
    max_tokens: int
    tools_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    uptime: Optional[float] = None


class ErrorResponse(BaseModel):
    """Response de error"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
