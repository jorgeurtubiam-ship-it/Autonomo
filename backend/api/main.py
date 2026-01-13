"""
FastAPI Backend - Main Application (Serves Frontend + API)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import time
import os
import logging

# Configurar Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/backend.log',
    filemode='a'
)
# Forzar nivel DEBUG para el proveedor de LLM y el Agente
logging.getLogger("agent").setLevel(logging.DEBUG)
logging.getLogger("backend.agent").setLevel(logging.DEBUG)

from .routes import chat_router, tools_router, config_router, conversations_router, vision_router
from .routes.chat import chat_websocket_endpoint

# Tiempo de inicio
start_time = time.time()

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Crear app
app = FastAPI(
    title="Agente Autónomo API",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers REST
app.include_router(chat_router)
app.include_router(tools_router)
app.include_router(config_router)
app.include_router(conversations_router)
app.include_router(vision_router)

# WebSocket
app.websocket("/ws/chat/{conversation_id}")(chat_websocket_endpoint)

@app.get("/health")
async def health_check():
    uptime = time.time() - start_time
    return {
        "status": "healthy",
        "service": "agent-api-combined",
        "uptime_seconds": round(uptime, 2)
    }

# Montar Frontend (para usar un solo túnel)
# Debe ir AL FINAL para no tapar otras rutas
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
