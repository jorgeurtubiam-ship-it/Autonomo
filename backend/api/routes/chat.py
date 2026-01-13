"""
Chat Routes - Endpoints para interactuar con el agente
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
import uuid
import logging

from ..models import ChatRequest, ChatResponse, ToolCallInfo
from ..dependencies import get_agent, get_storage_dependency, load_conversation_history
from agent import AgentCore
from storage import ConversationStorage

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/chat", tags=["chat"])


# WebSocket endpoint - DEBE ESTAR FUERA DEL ROUTER
# porque FastAPI no soporta WebSockets en routers con prefijos
async def chat_websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    agent: AgentCore = Depends(get_agent),
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """WebSocket para streaming de respuestas"""
    await websocket.accept()
    
    try:
        # Enviar confirmación de conexión
        await websocket.send_json({"type": "connected"})
        
        # No pre-creamos la conversación aquí para evitar ruido de chats vacíos
        # Se creará automáticamente al guardar el primer mensaje
        
        # Cargar historial de conversación
        load_conversation_history(conversation_id, agent, storage)
        
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")
            
            if msg_type == "approval_response":
                approved = data.get("approved", False)
                generator = agent.process_approval(conversation_id, approved)
                # No guardamos este "mensaje" del usuario en la BD como texto normal
                # pero el resultado sí se guardará en el bucle de abajo
            else:
                message = data.get("message", "")
                if not message:
                    continue
                
                # Guardar mensaje del usuario
                storage.save_message(conversation_id, "user", message)
                
                # Agregar al contexto del agente
                agent.context_manager.add_message("user", message, conversation_id)
                
                generator = agent.process_message(message, conversation_id)

            # Procesar mensaje y enviar eventos por WebSocket
            full_response_content = ""
            tool_calls_list = []
            iterations = 0

            async for event in generator:
                event_type = event.get("type")

                if event_type == "tool_call":
                    tool_call_info = ToolCallInfo(
                        id=event.get("tool_call_id", ""),
                        name=event.get("tool", ""),
                        arguments=event.get("arguments", {})
                    )
                    tool_calls_list.append(tool_call_info)
                    await websocket.send_json({
                        "type": "tool_call",
                        "tool": tool_call_info.name,
                        "arguments": tool_call_info.arguments,
                        "tool_call_id": tool_call_info.id
                    })
                elif event_type == "tool_result":
                    # Guardar resultado del tool en la base de datos
                    storage.save_message(
                        conversation_id,
                        "tool",
                        str(event.get("result") or event.get("error", "Error desconocido")),
                        tool_call_id=event.get("tool_call_id")
                    )
                    
                    await websocket.send_json({
                        "type": "tool_result",
                        "tool": event.get("tool"),
                        "tool_call_id": event.get("tool_call_id"),
                        "result": event.get("result"),
                        "error": event.get("error"),
                        "success": event.get("success", True)
                    })
                elif event_type == "message":
                    content_chunk = event.get("content", "")
                    full_response_content += content_chunk
                    await websocket.send_json({
                        "type": "message_chunk",
                        "content": content_chunk
                    })
                elif event_type == "thinking":
                    await websocket.send_json({
                        "type": "thinking",
                        "message": event.get("message", "Pensando..."),
                        "content": event.get("content", "")
                    })
                elif event_type == "approval_required":
                    await websocket.send_json({
                        "type": "approval_required",
                        "tool": event.get("tool"),
                        "arguments": event.get("arguments"),
                        "tool_id": event.get("tool_call_id"),
                        "message": event.get("message")
                    })
                elif event_type == "done":
                    iterations = event.get("iterations", 0)
                    await websocket.send_json({
                        "type": "done",
                        "iterations": iterations
                    })
            
            # Guardar respuesta completa del agente solo si hay contenido real
            if full_response_content.strip():
                storage.save_message(
                    conversation_id,
                    "assistant",
                    full_response_content,
                    tool_calls=[tc.model_dump() for tc in tool_calls_list] if tool_calls_list else None
                )
            elif tool_calls_list:
                # Si solo hubo tool calls, se guardan como assistant con contenido informativo
                storage.save_message(
                    conversation_id,
                    "assistant",
                    "Ejecutando herramientas...",
                    tool_calls=[tc.model_dump() for tc in tool_calls_list]
                )
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado (normalmente): {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for conversation {conversation_id}: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    agent: AgentCore = Depends(get_agent),
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Envía un mensaje al agente y obtiene respuesta
    
    - **message**: Mensaje del usuario
    - **conversation_id**: ID de conversación (opcional, se crea si no existe)
    - **stream**: Si hacer streaming (no implementado en REST, usar WebSocket)
    
    Los mensajes se guardan automáticamente en la base de datos.
    """
    try:
        # Generar conversation_id si no existe
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        # Crear conversación si no existe
        existing_conv = storage.get_conversation(conversation_id)
        if not existing_conv:
            # Crear conversación con título basado en el primer mensaje
            title = request.message[:50] if len(request.message) > 50 else request.message
            storage.create_conversation(conversation_id, title=title)
        
        # Cargar historial si existe
        try:
            load_conversation_history(conversation_id, agent, storage)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
        
        # Guardar mensaje del usuario
        storage.save_message(
            conversation_id,
            "user",
            request.message
        )
        
        # Procesar mensaje
        final_message = ""
        tool_calls_list = []
        iterations = 0
        
        async for event in agent.process_message(
            request.message,
            conversation_id
        ):
            event_type = event.get("type")
            
            if event_type == "tool_call":
                tool_calls_list.append(ToolCallInfo(
                    id=event.get("tool_call_id", ""),
                    name=event.get("tool", ""),
                    arguments=event.get("arguments", {})
                ))
            
            elif event_type == "tool_result":
                # Guardar resultado del tool en la base de datos
                storage.save_message(
                    conversation_id,
                    "tool",
                    str(event.get("result") or event.get("error", "Error desconocido")),
                    tool_call_id=event.get("tool_call_id")
                )
            
            elif event_type == "message":
                final_message = event.get("content", "")
            
            elif event_type == "done":
                iterations = event.get("iterations", 0)
        
        # Asegurar que tenemos un mensaje
        if not final_message:
            final_message = "Procesado sin respuesta"
        
        # Guardar respuesta del agente
        try:
            storage.save_message(
                conversation_id,
                "assistant",
                final_message,
                tool_calls=[tc.model_dump() for tc in tool_calls_list] if tool_calls_list else None
            )
        except Exception as e:
            print(f"Warning: Could not save response: {e}")
        
        # Crear response
        response = ChatResponse(
            conversation_id=conversation_id,
            message=final_message,
            tool_calls=tool_calls_list if tool_calls_list else None,
            iterations=iterations
        )
        
        return response
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {conversation_id}")
    except Exception as e:
        import traceback
        logger.error(f"Error en WebSocket {conversation_id}: {e}")
        traceback.print_exc()
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass


@router.get("/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Obtiene el historial de una conversación desde la base de datos
    
    - **conversation_id**: ID de la conversación
    """
    try:
        messages = storage.get_messages(conversation_id)
        
        # Si no hay mensajes, retornamos lista vacía en lugar de 404
        # para evitar ruidos en el terminal y permitir estados iniciales
        if messages is None:
            messages = []
        
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": msg.tool_calls,
                    "created_at": msg.created_at
                }
                for msg in messages
            ],
            "total": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )
