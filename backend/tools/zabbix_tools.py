"""
Zabbix Tools - Herramientas para interactuar con la API de Zabbix
"""

import aiohttp
import json
import logging
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ZabbixAlertsParams(BaseModel):
    """Parámetros para zabbix_get_alerts"""
    priority_min: int = Field(
        default=2, 
        description="Prioridad mínima de las alertas (0-5). 2=Warning, 4=High, 5=Disaster."
    )
    limit: int = Field(
        default=10, 
        description="Número máximo de alertas a retornar."
    )

class ZabbixTool:
    """Tool para que el agente consulte alertas y estados en Zabbix"""
    
    name = "zabbix_get_alerts"
    description = "Consulta la API de Zabbix para obtener una lista de alertas (triggers) activas. Úsalo para conocer el estado de salud de la infraestructura monitoreada."
    category = "observability"
    
    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        # Intentar obtener de variables de entorno o usar valores por defecto (ejemplo local)
        self.url = url or os.getenv("ZABBIX_URL", "http://localhost/zabbix/api_jsonrpc.php")
        self.user = user or os.getenv("ZABBIX_USER", "Admin")
        self.password = password or os.getenv("ZABBIX_PASSWORD", "zabbix")
        self.auth_token = None

    async def _authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Autentica con la API de Zabbix y guarda el token"""
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": 1,
            "auth": None
        }
        
        try:
            async with session.post(self.url, json=payload) as response:
                if response.status != 200:
                    return False
                
                result = await response.json()
                if "result" in result:
                    self.auth_token = result["result"]
                    return True
                return False
        except Exception as e:
            logger.error(f"Error autenticando en Zabbix: {e}")
            return False

    async def execute(self, priority_min: int = 2, limit: int = 10) -> Dict[str, Any]:
        """
        Consulta triggers activos en Zabbix
        """
        async with aiohttp.ClientSession() as session:
            # 1. Autenticar si no tenemos token
            if not self.auth_token:
                success = await self._authenticate(session)
                if not success:
                    return {
                        "success": False,
                        "error": "No se pudo autenticar con la API de Zabbix. Verifica URL y credenciales.",
                        "details": f"URL: {self.url}, User: {self.user}"
                    }
            
            # 2. Consultar triggers
            payload = {
                "jsonrpc": "2.0",
                "method": "trigger.get",
                "params": {
                    "output": ["triggerid", "description", "priority", "lastchange"],
                    "filter": {
                        "value": 1  # Solo triggers activos (PROBLEM)
                    },
                    "min_priority": priority_min,
                    "selectHosts": ["hostid", "name"],
                    "sortfield": "priority",
                    "sortorder": "DESC",
                    "limit": limit
                },
                "auth": self.auth_token,
                "id": 2
            }
            
            try:
                async with session.post(self.url, json=payload) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Error HTTP {response.status}"}
                    
                    result = await response.json()
                    triggers = result.get("result", [])
                    
                    formatted_alerts = []
                    for t in triggers:
                        host_name = t.get("hosts", [{}])[0].get("name", "Unknown Host")
                        priority_map = {
                            "0": "Not classified",
                            "1": "Information",
                            "2": "Warning",
                            "3": "Average",
                            "4": "High",
                            "5": "Disaster"
                        }
                        prio_text = priority_map.get(str(t.get("priority")), "Unknown")
                        
                        formatted_alerts.append({
                            "host": host_name,
                            "alert": t.get("description"),
                            "priority": prio_text,
                            "trigger_id": t.get("triggerid")
                        })
                    
                    return {
                        "success": True,
                        "count": len(formatted_alerts),
                        "alerts": formatted_alerts
                    }
            except Exception as e:
                logger.error(f"Error consultando Zabbix: {e}")
                return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "priority_min": {
                        "type": "integer",
                        "description": "Prioridad mínima (0-5). 2=Warning, 4=High, 5=Disaster."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de alertas a mostrar."
                    }
                }
            }
        }
