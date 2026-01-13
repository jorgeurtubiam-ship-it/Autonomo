"""
Modelos de API
"""

from .requests import ChatRequest, ConfigUpdate, ConversationCreate
from .responses import (
    ChatResponse,
    ConversationInfo,
    ConversationList,
    ToolInfo,
    ToolsList,
    ConfigResponse,
    HealthResponse,
    ErrorResponse,
    ToolCallInfo
)

__all__ = [
    # Requests
    "ChatRequest",
    "ConfigUpdate",
    "ConversationCreate",
    
    # Responses
    "ChatResponse",
    "ConversationInfo",
    "ConversationList",
    "ToolInfo",
    "ToolsList",
    "ConfigResponse",
    "HealthResponse",
    "ErrorResponse",
    "ToolCallInfo",
]
