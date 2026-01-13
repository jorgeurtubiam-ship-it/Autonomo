"""
Nagios Tools - Herramientas para interactuar con Nagios Monitoring
"""

import aiohttp
import logging
import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class NagiosTool:
    """Tool para obtener alertas y estado de Nagios"""
    
    name = "nagios_get_alerts"
    description = "Obtiene alertas críticas y advertencias de Nagios Monitoring. Retorna un resumen de estados y lista de problemas."
    category = "observability"

    def __init__(self, url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        # Intentar obtener de variables de entorno o usar defaults del script del usuario
        self.base_url = url or os.getenv("NAGIOS_URL", "http://localhost:8080/nagios")
        self.user = user or os.getenv("NAGIOS_USER", "nagiosadmin")
        self.password = password or os.getenv("NAGIOS_PASSWORD", "nagios@2025")

    async def execute(self, query_type: str = "servicecount", url: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta la API JSON de Nagios (statusjson.cgi)
        """
        # Prioridad: Parámetro > Env Var > Default
        target_url = url or self.base_url
        target_user = user or self.user
        target_password = password or self.password

        # Asegurar que apunta al CGI
        if "statusjson.cgi" in target_url:
            api_url = target_url
        else:
            base = target_url.rstrip('/')
            if base.endswith('cgi-bin'):
                api_url = f"{base}/statusjson.cgi"
            elif base.endswith('/nagios'):
                api_url = f"{base}/cgi-bin/statusjson.cgi"
            else:
                # Intento genérico
                api_url = f"{base}/nagios/cgi-bin/statusjson.cgi" if "/nagios" not in base else f"{base}/cgi-bin/statusjson.cgi"

        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(target_user, target_password)
            
            try:
                logger.info(f"Consultando Nagios en: {api_url}")
                # 1. Obtener conteos (Resumen)
                async with session.get(f"{api_url}?query=servicecount", auth=auth, timeout=10) as resp:
                    if resp.status != 200:
                        return {
                            "success": False, 
                            "error": f"Nagios retornó status {resp.status}", 
                            "url": api_url,
                            "hint": "Verifica que el usuario y contraseña sean correctos y que la URL sea accesible."
                        }
                    
                    data = await resp.json()
                    counts = data.get('data', {}).get('count', {})
                    
                # 2. Obtener lista de servicios con problemas
                async with session.get(f"{api_url}?query=servicelist", auth=auth, timeout=10) as resp:
                    if resp.status == 200:
                        list_data = await resp.json()
                        services = list_data.get('data', {}).get('servicelist', {})
                        
                        # Filtrar problemas (status > 0)
                        problems = []
                        for s_key, s_val in services.items():
                            if s_val.get('status', 0) > 0:
                                problems.append({
                                    "host": s_val.get('host_name'),
                                    "service": s_val.get('description'),
                                    "status": s_val.get('status'),
                                    "output": s_val.get('plugin_output')
                                })
                    else:
                        problems = []

                return {
                    "success": True,
                    "summary": {
                        "ok": counts.get('ok', 0),
                        "warning": counts.get('warning', 0),
                        "critical": counts.get('critical', 0),
                        "unknown": counts.get('unknown', 0),
                        "total": counts.get('all', 0)
                    },
                    "problems": problems[:20], # Limitar a los primeros 20
                    "count": counts.get('critical', 0) + counts.get('warning', 0)
                }

            except Exception as e:
                logger.error(f"Error consultando Nagios: {e}")
                return {"success": False, "error": str(e), "url": api_url}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "description": "Tipo de consulta (servicecount, hostcount, servicelist).",
                        "default": "servicecount"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL base de Nagios (ej: http://localhost:8080/nagios)"
                    },
                    "user": {
                        "type": "string",
                        "description": "Usuario de Nagios"
                    },
                    "password": {
                        "type": "string",
                        "description": "Contraseña de Nagios"
                    }
                }
            }
        }
