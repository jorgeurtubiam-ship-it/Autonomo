"""
WebSocket para Chat en Tiempo Real
Permite streaming de respuestas del agente
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio

from ..dependencies import get_agent
from agent import AgentCore


class ConnectionManager:
    """Gestiona las conexiones WebSocket activas"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Acepta una nueva conexión"""
        await websocket.accept()
        
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        
        self.active_connections[conversation_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Elimina una conexión"""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
            
            # Limpiar si no hay más conexiones
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
    
    async def send_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje a un websocket específico"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
    
    async def broadcast(self, message: dict, conversation_id: str):
        """Envía un mensaje a todos los websockets de una conversación"""
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await self.send_message(message, connection)


# Singleton del manager
manager = ConnectionManager()


async def websocket_chat_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    agent: AgentCore = Depends(get_agent)
):
    """
    WebSocket endpoint para chat en tiempo real
    
    URL: ws://localhost:8000/ws/chat/{conversation_id}
    
    Eventos enviados al cliente:
    - connected: Conexión establecida
    - thinking: Agente está pensando
    - tool_call: Se va a ejecutar un tool
    - tool_result: Resultado de tool
    - message: Respuesta del agente
    - error: Error durante procesamiento
    - done: Procesamiento completado
    """
    
    await manager.connect(websocket, conversation_id)
    
    try:
        # Enviar confirmación de conexión
        await manager.send_message({
            "type": "connected",
            "conversation_id": conversation_id,
            "message": "Conexión establecida"
        }, websocket)
        
        # Loop principal
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message")
            
            if not user_message:
                await manager.send_message({
                    "type": "error",
                    "error": "Mensaje vacío"
                }, websocket)
                continue
            
            # Procesar mensaje con el agente
            try:
                async for event in agent.process_message(user_message, conversation_id):
                    # Enviar cada evento al cliente
                    await manager.send_message(event, websocket)
                
            except Exception as e:
                await manager.send_message({
                    "type": "error",
                    "error": str(e)
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        print(f"Cliente desconectado de conversación {conversation_id}")
    
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(websocket, conversation_id)
