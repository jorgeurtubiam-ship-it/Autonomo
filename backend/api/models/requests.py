"""
Modelos de Request para la API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request para enviar mensaje al agente"""
    message: str = Field(..., description="Mensaje del usuario")
    conversation_id: Optional[str] = Field(None, description="ID de la conversación (se crea si no existe)")
    stream: bool = Field(False, description="Si hacer streaming de la respuesta")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Crea un archivo hello.txt con 'Hola Mundo'",
                "conversation_id": "conv_123",
                "stream": False
            }
        }


class ConfigUpdate(BaseModel):
    """Request para actualizar configuración"""
    llm_provider: Optional[str] = Field(None, description="Proveedor de LLM (openai, anthropic, deepseek, ollama)")
    model: Optional[str] = Field(None, description="Modelo a usar")
    autonomy_level: Optional[str] = Field(None, description="Nivel de autonomía (full, semi, supervised)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperatura del modelo")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "llm_provider": "ollama",
                "model": "llama3.2:latest",
                "autonomy_level": "semi",
                "temperature": 0.7
            }
        }


class ConversationCreate(BaseModel):
    """Request para crear conversación"""
    title: Optional[str] = Field(None, description="Título de la conversación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Nueva conversación"
            }
        }
