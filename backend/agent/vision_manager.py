"""
Vision Manager - Gestión de visión y procesamiento de frames
"""

import cv2
import base64
import numpy as np
from PIL import Image
import io
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class VisionManager:
    """
    Gestiona la recepción, almacenamiento y procesamiento de frames de video.
    Incluye lógica de "Auto-Snapshot" para capturar momentos clave.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.current_frame: Optional[np.ndarray] = None
        self.last_update: Optional[datetime] = None
        self.last_snapshot: Optional[np.ndarray] = None
        self.last_snapshot_time: Optional[datetime] = None
        
        # Umbral para auto-snapshot (milisegundos entre capturas)
        self.snapshot_interval_ms = 2000 
        
        self.annotations: List[Dict[str, Any]] = []
        self._initialized = True
        logger.info("VisionManager inicializado con Auto-Snapshot")
        
    def update_frame(self, frame_data: np.ndarray):
        """Actualiza el frame actual y evalúa si debe tomar un snapshot"""
        self.current_frame = frame_data
        self.last_update = datetime.now()
        
        # Lógica simple de Auto-Snapshot: Cada X segundos si hay video activo
        if self.last_snapshot_time is None or \
           (datetime.now() - self.last_snapshot_time).total_seconds() * 1000 > self.snapshot_interval_ms:
            logger.info(f"Triggering Auto-Snapshot. Current frame shape: {self.current_frame.shape if self.current_frame is not None else 'None'}")
            self.take_snapshot()
            
    def take_snapshot(self):
        """Captura el frame actual como un snapshot oficial para la IA"""
        if self.current_frame is not None:
            self.last_snapshot = self.current_frame.copy()
            self.last_snapshot_time = datetime.now()
            logger.info(f"✅ Auto-Snapshot capturado a las {self.last_snapshot_time.strftime('%H:%M:%S')}")

    def get_current_frame_b64(self, use_snapshot: bool = True, quality: int = 80) -> Optional[str]:
        """Obtiene el frame (o el último snapshot) en formato base64"""
        frame = self.last_snapshot if use_snapshot else self.current_frame
        
        if frame is None:
            logger.warning("get_current_frame_b64: Frame is None")
            return None
            
        # Log del tamaño del frame original
        h, w = frame.shape[:2]
        logger.info(f"Processing frame. Original Shape: {w}x{h}")
            
        # Redimensionar si es muy grande (max 1280px de ancho/alto)
        # Esto ayuda a que el modelo de visión responda más rápido y no falle por timeout
        max_dim = 1280
        if w > max_dim or h > max_dim:
            if w > h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.info(f"Frame resized to: {new_w}x{new_h}")

        # Convertir de BGR (OpenCV) a RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        
        # Guardar en buffer como JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def get_active_annotations(self, ttl_seconds: int = 15) -> List[Dict[str, Any]]:
        """Retorna anotaciones que no han expirado y limpia las antiguas"""
        now = datetime.now()
        self.annotations = [a for a in self.annotations if (now - a["timestamp"]).total_seconds() < ttl_seconds]
        
        # Eliminar datetime antes de enviar por JSON
        safe_annotations = []
        for a in self.annotations:
            clean_a = a.copy()
            clean_a["timestamp"] = clean_a["timestamp"].isoformat()
            safe_annotations.append(clean_a)
            
        return safe_annotations

    def add_annotation(self, type: str, x: int, y: int, color: str = "#ff0000", label: str = ""):
        """
        Agrega una anotación visual. 
        x, y deben ser porcentajes (0-100) para ser independientes de la resolución del móvil.
        """
        self.annotations.append({
            "type": type,
            "x": x,
            "y": y,
            "color": color,
            "label": label,
            "timestamp": datetime.now()
        })
        logger.info(f"📍 Anotación añadida en ({x}%, {y}%): {label}")

    def clear_annotations(self):
        """Limpia las anotaciones actuales"""
        self.annotations = []

    def get_status(self) -> Dict[str, Any]:
        """Retorna el estado actual de la visión"""
        return {
            "active": self.current_frame is not None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "last_snapshot": self.last_snapshot_time.isoformat() if self.last_snapshot_time else None,
            "annotation_count": len(self.annotations)
        }

# Instancia global
vision_manager = VisionManager()
