"""
Checkmk Tools - Herramientas para interactuar con la API REST de Checkmk
"""

import aiohttp
import logging
import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CheckmkAlertsParams(BaseModel):
    """Parámetros para checkmk_get_alerts"""
    site: str = Field(..., description="Nombre del sitio de Checkmk.")

class CheckmkTool:
    """Tool para que el agente consulte problemas en Checkmk"""
    
    name = "checkmk_get_alerts"
    description = "Consulta la API de Checkmk para obtener una lista de servicios con problemas (CRIT/WARN/UNKNOWN). Úsalo para conocer la salud de los servicios monitoreados."
    category = "observability"
    
    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, secret: Optional[str] = None):
        self.url = url or os.getenv("CHECKMK_URL", "http://localhost/check_mk/api/1.0/")
        self.user = user or os.getenv("CHECKMK_USER", "automation")
        self.secret = secret or os.getenv("CHECKMK_SECRET", "your_automation_secret")
        self.base_url = self.url.rstrip('/')

    async def execute(self, site: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta problemas actuales en Checkmk
        Endpoint: domain-types/service/collections/all con filtros (state != 0)
        """
        # Si la URL ya incluye el sitio, no necesitamos añadirlo
        # Checkmk API URL suele ser: http://<server>/<site>/check_mk/api/1.0/
        api_url = f"{self.base_url}/domain-types/service/collections/all"
        
        headers = {
            "Authorization": f"Bearer {self.user} {self.secret}",
            "Accept": "application/json"
        }
        
        # Filtro para solo mostrar problemas (0=OK, 1=WARN, 2=CRIT, 3=UNKNOWN)
        params = {
            "query": json.dumps({"op": "!=", "left": "state", "right": 0})
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(f"CheckmkTool: Consultando alertas en {api_url}")
                async with session.get(api_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        services = data.get("value", [])
                        
                        formatted_alerts = []
                        for s in services:
                            ext = s.get("extensions", {})
                            state_map = {0: "OK", 1: "WARN", 2: "CRIT", 3: "UNKNOWN"}
                            state = ext.get("state", -1)
                            
                            formatted_alerts.append({
                                "host": ext.get("host_name"),
                                "service": ext.get("description"),
                                "state": state_map.get(state, f"CODE {state}"),
                                "output": ext.get("plugin_output")
                            })
                            
                        return {
                            "success": True,
                            "count": len(formatted_alerts),
                            "alerts": formatted_alerts
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Error {response.status}: {error_text}"}
            except Exception as e:
                logger.error(f"Error en CheckmkTool: {e}")
                return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "site": {
                        "type": "string",
                        "description": "Nombre del sitio (si no está en la URL base)."
                    }
                }
            }
        }

class CheckmkListHostsTool:
    """Tool para listar hosts en Checkmk"""
    
    name = "checkmk_list_hosts"
    description = "Lista todos los hosts configurados en Checkmk y su estado de monitoreo."
    category = "observability"

    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, secret: Optional[str] = None):
        self.url = url or os.getenv("CHECKMK_URL", "http://localhost/check_mk/api/1.0/")
        self.user = user or os.getenv("CHECKMK_USER", "automation")
        self.secret = secret or os.getenv("CHECKMK_SECRET", "your_automation_secret")
        self.base_url = self.url.rstrip('/')

    async def execute(self) -> Dict[str, Any]:
        """
        Lista todos los hosts
        Endpoint: domain-types/host_config/collections/all
        """
        api_url = f"{self.base_url}/domain-types/host_config/collections/all"
        headers = {
            "Authorization": f"Bearer {self.user} {self.secret}",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        hosts = data.get("value", [])
                        formatted_hosts = [h.get("id") for h in hosts]
                        return {
                            "success": True,
                            "count": len(formatted_hosts),
                            "hosts": formatted_hosts
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
                "properties": {}
            }
        }
