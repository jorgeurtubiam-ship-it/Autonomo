"""
Rundeck Tools - Herramientas para interactuar con la API de Rundeck
"""

import aiohttp
import logging
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class RundeckJobParams(BaseModel):
    """Parámetros para rundeck_run_job"""
    job_id: str = Field(..., description="ID del job de Rundeck a ejecutar.")
    argString: Optional[str] = Field(default=None, description="Argumentos para el job (ej: '-env prod -force true').")

class RundeckTool:
    """Tool para que el agente gestione jobs en Rundeck"""
    
    name = "rundeck_run_job"
    description = "Ejecuta un job específico en Rundeck por su ID. Úsalo para disparar automatizaciones existentes como backups, despliegues o limpiezas."
    category = "automation"
    
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = url or os.getenv("RUNDECK_URL", "http://localhost:4440")
        self.token = token or os.getenv("RUNDECK_TOKEN", "your_rundeck_api_token")
        # Asegurar que la URL termine correctamente para concatenar con /api/...
        self.base_url = self.url.rstrip('/')

    async def execute(self, job_id: str, argString: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta un job en Rundeck
        """
        api_url = f"{self.base_url}/api/41/job/{job_id}/run"
        headers = {
            "X-Rundeck-Auth-Token": self.token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = {}
        if argString:
            payload["argString"] = argString
            
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(f"RundeckTool: Ejecutando job {job_id} en {api_url}")
                async with session.post(api_url, headers=headers, json=payload) as response:
                    if response.status == 200 or response.status == 201:
                        result = await response.json()
                        execution_id = result.get("id")
                        return {
                            "success": True,
                            "message": f"Job {job_id} iniciado exitosamente.",
                            "execution_id": execution_id,
                            "status": result.get("status"),
                            "permalink": result.get("permalink")
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Error de Rundeck (HTTP {response.status}): {error_text}"
                        }
            except Exception as e:
                logger.error(f"Error en RundeckTool: {e}")
                return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID del job a ejecutar."
                    },
                    "argString": {
                        "type": "string",
                        "description": "Argumentos opcionales para el job."
                    }
                },
                "required": ["job_id"]
            }
        }

class RundeckListTool:
    """Tool para listar jobs de un proyecto en Rundeck"""
    
    name = "rundeck_list_jobs"
    description = "Lista los jobs disponibles en un proyecto de Rundeck. Úsalo para descubrir qué automatizaciones puedes ejecutar."
    category = "automation"

    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        self.url = url or os.getenv("RUNDECK_URL", "http://localhost:4440")
        self.token = token or os.getenv("RUNDECK_TOKEN", "your_rundeck_api_token")
        self.base_url = self.url.rstrip('/')

    async def execute(self, project: str) -> Dict[str, Any]:
        """
        Lista jobs de un proyecto
        """
        api_url = f"{self.base_url}/api/41/project/{project}/jobs"
        headers = {
            "X-Rundeck-Auth-Token": self.token,
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        jobs = await response.json()
                        formatted_jobs = []
                        for j in jobs:
                            formatted_jobs.append({
                                "id": j.get("id"),
                                "name": j.get("name"),
                                "group": j.get("group"),
                                "description": j.get("description")
                            })
                        return {
                            "success": True,
                            "project": project,
                            "count": len(formatted_jobs),
                            "jobs": formatted_jobs
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Error {response.status}: {error_text}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Nombre del proyecto en Rundeck."
                    }
                },
                "required": ["project"]
            }
        }
