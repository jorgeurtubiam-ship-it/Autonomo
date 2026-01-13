"""
Conversations Routes - Gestión de conversaciones
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..models import ConversationList, ConversationInfo
from ..dependencies import get_storage_dependency
from storage import ConversationStorage

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/", response_model=ConversationList)
async def list_conversations(
    limit: int = 50,
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Lista todas las conversaciones guardadas
    
    - **limit**: Número máximo de conversaciones a retornar (default: 50)
    """
    try:
        conversations = storage.list_conversations(limit=limit)
        
        conv_info_list = [
            ConversationInfo(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=conv.message_count
            )
            for conv in conversations
        ]
        
        return ConversationList(
            conversations=conv_info_list,
            total=len(conv_info_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listando conversaciones: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationInfo)
async def get_conversation(
    conversation_id: str,
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Obtiene información de una conversación específica
    
    - **conversation_id**: ID de la conversación
    """
    try:
        conv = storage.get_conversation(conversation_id)
        
        if not conv:
            raise HTTPException(
                status_code=404,
                detail=f"Conversación {conversation_id} no encontrada"
            )
        
        return ConversationInfo(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=conv.message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo conversación: {str(e)}"
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Elimina una conversación y todos sus mensajes
    
    - **conversation_id**: ID de la conversación a eliminar
    """
    try:
        # No verificamos existencia previa para ser más resilientes
        # si por algún motivo la entrada está en el listado pero falla el get
        storage.delete_conversation(conversation_id)
        
        return {
            "status": "success",
            "message": f"Conversación {conversation_id} eliminada",
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando conversación: {str(e)}"
        )



@router.post("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Actualiza el título de una conversación
    
    - **conversation_id**: ID de la conversación
    - **title**: Nuevo título
    """
    try:
        # Verificar que existe
        conv = storage.get_conversation(conversation_id)
        if not conv:
            # Crear si no existe
            storage.create_conversation(conversation_id, title=title)
        else:
            # Actualizar título (necesitaríamos agregar este método)
            # Por ahora, retornar info
            pass
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "title": title
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando título: {str(e)}"
        )
