"""
Dremio Tools - Herramientas para interactuar con la API de Dremio Data Lake
"""

import aiohttp
import asyncio
import logging
import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DremioQueryTool:
    """Tool para ejecutar consultas SQL en Dremio"""
    
    name = "dremio_query"
    description = "Ejecuta una consulta SQL en Dremio Data Lake. Retorna los resultados formateados. Úsalo para extraer datos para análisis."
    category = "data"
    
    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.hostname = url or os.getenv("DREMIO_HOSTNAME", "http://localhost:9047")
        self.user = user or os.getenv("DREMIO_USER", "dremio")
        self.password = password or os.getenv("DREMIO_PASSWORD", "dremio123")
        self.token = None

    async def _authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Autentica con la API v2 para obtener el token"""
        login_url = f"{self.hostname}/apiv2/login"
        payload = {"userName": self.user, "password": self.password}
        
        try:
            async with session.post(login_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error autenticando en Dremio: {e}")
            return False

    async def execute(self, sql: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Ejecuta SQL, espera al Job y retorna resultados
        """
        async with aiohttp.ClientSession() as session:
            if not self.token:
                if not await self._authenticate(session):
                    return {"success": False, "error": "No se pudo autenticar en Dremio."}
            
            headers = {
                "Authorization": f"_dremio{self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # 1. Enviar Query
            query_url = f"{self.hostname}/api/v3/sql"
            payload = {"sql": sql}
            if context:
                payload["context"] = context
                
            async with session.post(query_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    return {"success": False, "error": f"Error iniciando query: {await response.text()}"}
                job_id = (await response.json()).get("id")
            
            # 2. Monitorear Job (Poll simplificado)
            max_retries = 30
            for _ in range(max_retries):
                job_url = f"{self.hostname}/api/v3/job/{job_id}"
                async with session.get(job_url, headers=headers) as response:
                    job_data = await response.json()
                    state = job_data.get("jobState")
                    
                    if state == "COMPLETED":
                        # 3. Obtener Resultados
                        results_url = f"{self.hostname}/api/v3/job/{job_id}/results"
                        async with session.get(results_url, headers=headers) as res_response:
                            return {
                                "success": True,
                                "job_id": job_id,
                                "data": await res_response.json()
                            }
                    elif state in ["FAILED", "CANCELED"]:
                        return {"success": False, "error": f"Job {state}: {job_data.get('errorMessage')}"}
                
                await asyncio.sleep(1)
                
            return {"success": False, "error": "Tiempo de espera agotado esperando el Job de Dremio."}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "Consulta SQL a ejecutar."},
                    "context": {"type": "array", "items": {"type": "string"}, "description": "Contexto opcional (fuente/espacio)."}
                },
                "required": ["sql"]
            }
        }

class DremioCatalogTool:
    """Tool para explorar el catálogo de Dremio"""
    
    name = "dremio_list_catalog"
    description = "Lista el catálogo de Dremio (fuentes, espacios, datasets). Úsalo para explorar qué datos están disponibles."
    category = "data"

    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.hostname = url or os.getenv("DREMIO_HOSTNAME", "http://localhost:9047")
        self.user = user or os.getenv("DREMIO_USER", "dremio")
        self.password = password or os.getenv("DREMIO_PASSWORD", "dremio123")
        self.token = None

    async def execute(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            # Reutilizar lógica de auth (simplificado aquí para brevedad)
            login_url = f"{self.hostname}/apiv2/login"
            async with session.post(login_url, json={"userName": self.user, "password": self.password}) as response:
                if response.status != 200: return {"success": False, "error": "Auth failed"}
                token = (await response.json()).get("token")
            
            headers = {"Authorization": f"_dremio{token}", "Accept": "application/json"}
            async with session.get(f"{self.hostname}/api/v3/catalog", headers=headers) as response:
                if response.status == 200:
                    return {"success": True, "catalog": (await response.json()).get("data", [])}
                return {"success": False, "error": await response.text()}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": {}}
        }
