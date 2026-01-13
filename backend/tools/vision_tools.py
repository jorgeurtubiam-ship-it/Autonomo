"""
Vision Tools - Herramientas para que el agente pueda "ver"
"""

import aiohttp
import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Importar el VisionManager para obtener frames
from agent.vision_manager import vision_manager

logger = logging.getLogger(__name__)

class GetVisualContextParams(BaseModel):
    """Parámetros para get_visual_context"""
    prompt: Optional[str] = Field(
        default="Describe lo que ves en esta imagen detalladamente.", 
        description="Qué debe buscar o analizar la IA en la imagen."
    )

class VisionTool:
    """Tool para que el agente obtenga contexto visual desde la cámara móvil"""
    
    name = "get_visual_context"
    description = "Captura una imagen actual de la cámara del móvil y la analiza para responder preguntas visuales. Úsalo cuando necesites saber qué hay frente a la cámara."
    category = "vision"
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url

    async def execute(self, prompt: str = "Describe lo que ves en esta imagen detalladamente.") -> Dict[str, Any]:
        """
        Captura el frame actual y lo envía a un modelo de visión local
        """
        try:
            # 1. Obtener imagen en base64 del VisionManager
            image_b64 = vision_manager.get_current_frame_b64(use_snapshot=True)
            
            if not image_b64:
                return {
                    "success": False,
                    "error": "No hay señal de video activa. Asegúrate de que el móvil esté transmitiendo.",
                    "instruction": "Pide al usuario que active la cámara desde el botón 'Activar Visión' en la interfaz."
                }
            
            # 2. Llamar a Ollama con el modelo moondream
            # Moondream es excelente para descripciones rápidas y precisas
            payload = {
                "model": "moondream:latest",
                "prompt": prompt,
                "stream": False,
                "images": [image_b64]
            }
            
            logger.info(f"VisionTool Calling Ollama (moondream) with prompt: '{prompt}' (Image B64 length: {len(image_b64)})")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error en Ollama (Vision): {error_text}")
                        return {
                            "success": False,
                            "error": f"Error en el modelo de visión (Ollama): {error_text}"
                        }
                    
                    result = await response.json()
                    logger.info(f"VisionTool Ollama Raw Response: {json.dumps(result)}")
                    description = result.get("response", "").strip()
                    
                    if not description:
                        description = "El modelo no proporcionó una descripción de la imagen."
                        logger.warning("VisionTool: Ollama devolvió una respuesta vacía.")
            
            return {
                "success": True,
                "description": description,
                "timestamp": vision_manager.last_snapshot_time.isoformat() if vision_manager.last_snapshot_time else None
            }
            
        except Exception as e:
            logger.error(f"Error en VisionTool: {str(e)}")
            return {
                "success": False,
                "error": f"Error procesando visión: {str(e)}"
            }

    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Explica qué quieres que la IA busque en la cámara (ej: '¿Hay algún error en mi monitor?', '¿Qué dice este documento?')"
                    }
                }
            }
        }

class VisionPointTool:
    """Tool para que el agente señale objetos en la pantalla del móvil"""
    
    name = "point_to_object"
    description = "Dibuja una marca visual (punto/círculo) en la pantalla del móvil del usuario para señalar un objeto específico."
    category = "vision"

    async def execute(self, x: int, y: int, label: str = "", color: str = "#ff0000", **kwargs) -> Dict[str, Any]:
        """
        Envía una instrucción de dibujo al VisionManager
        """
        try:
            vision_manager.add_annotation(
                type="point",
                x=x,
                y=y,
                color=color,
                label=label
            )
            return {
                "success": True,
                "message": f"Marcador '{label}' colocado en ({x}%, {y}%)",
                "x": x,
                "y": y
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "Coordenada Horizontal en porcentaje (0-100). De izquierda (0) a derecha (100)."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Coordenada Vertical en porcentaje (0-100). De arriba (0) a abajo (100)."
                    },
                    "label": {
                        "type": "string",
                        "description": "Texto breve que aparecerá junto al marcador (ej: 'El error está aquí')"
                    },
                    "color": {
                        "type": "string",
                        "description": "Color del marcador en formato hex (ej: '#ff0000' para rojo, '#00ff00' para verde)"
                    }
                },
                "required": ["x", "y"]
            }
        }
