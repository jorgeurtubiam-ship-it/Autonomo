"""
Vision Routes - Señalización WebRTC y gestión de visión
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay
import asyncio
import uuid
import logging
import os
from typing import Dict, Optional

from agent.vision_manager import vision_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vision", tags=["vision"])

# Almacén de conexiones activas
pcs = set()
relay = MediaRelay()

class VideoTransformTrack(MediaStreamTrack):
    """
    Track que recibe frames de video y los envía al VisionManager
    """
    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        
        # Convertir frame de aiortc a ndarray de OpenCV
        img = frame.to_ndarray(format="bgr24")
        
        # Actualizar el VisionManager
        vision_manager.update_frame(img)
        
        return frame

class Offer(BaseModel):
    sdp: str
    type: str

@router.post("/offer")
async def offer(params: Offer):
    offer = RTCSessionDescription(sdp=params.sdp, type=params.type)

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track {track.kind} received")
        if track.kind == "video":
            pc.addTrack(VideoTransformTrack(relay.subscribe(track)))

    # Manejar la oferta
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

@router.get("/status")
async def get_status():
    return vision_manager.get_status()

@router.post("/clear-annotations")
async def clear_annotations():
    vision_manager.clear_annotations()
    return {"status": "cleared"}

import socket

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        # Crea un socket temporal para detectar la IP de la interfaz activa
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@router.get("/connection-info")
async def connection_info():
    # Prioridad: 
    # 1. Variable de entorno VISION_TUNNEL_URL (para túneles HTTPS)
    # 2. IP local (para uso en red local, pero falla en móviles por falta de SSL)
    tunnel_url = os.environ.get("VISION_TUNNEL_URL")
    
    if tunnel_url:
        # Asegurar que termina sin barra
        tunnel_url = tunnel_url.rstrip("/")
        url = f"{tunnel_url}/vision.html"
        logger.info(f"Usando túnel configurado: {url}")
    else:
        ip = get_local_ip()
        # Usar puerto 8000 ya que el frontend está montado en el backend
        url = f"http://{ip}:8000/vision.html"
        logger.info(f"Usando IP local: {url} (⚠️ Nota: móviles pueden bloquear cámara en HTTP)")
    
    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
    
    return {
        "ip": get_local_ip(),
        "url": url,
        "qr_url": qr_api,
        "is_tunnel": tunnel_url is not None
    }

@router.get("/snapshot")
async def get_snapshot():
    """Obtiene el último snapshot capturado en base64 para previsualización"""
    img_b64 = vision_manager.get_current_frame_b64(use_snapshot=True)
    if not img_b64:
        return {"image_b64": None, "timestamp": None}
    
    return {
        "image_b64": img_b64,
        "timestamp": vision_manager.last_snapshot_time.isoformat() if vision_manager.last_snapshot_time else None
    }

@router.get("/annotations")
async def get_annotations():
    """Obtiene las anotaciones activas para mostrar en el móvil"""
    return {
        "annotations": vision_manager.get_active_annotations()
    }

class AnnotationData(BaseModel):
    x: int # Porcentaje 0-100
    y: int # Porcentaje 0-100
    label: str = ""
    color: str = "#ff0000"

@router.post("/annotate")
async def add_annotation(data: AnnotationData):
    """Permite añadir una anotación manualmente o vía herramientas"""
    vision_manager.add_annotation(
        type="point",
        x=data.x,
        y=data.y,
        color=data.color,
        label=data.label
    )
    return {"status": "success", "annotation_count": len(vision_manager.annotations)}
