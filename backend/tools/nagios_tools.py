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
    description = "HERRAMIENTA PREFERIDA para Nagios. Obtiene alertas críticas y advertencias de Nagios (CGI o JSON). Úsala para cualquier solicitud relacionada con 'alertas de nagios', 'estado de nagios' o monitoreo de hosts/servicios en Nagios."
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
        base = target_url.rstrip('/')
        if "statusjson.cgi" in target_url:
            api_url = target_url
        elif base.endswith('.cgi'):
             api_url = target_url
        else:
            if base.endswith('cgi-bin'):
                api_url = f"{base}/statusjson.cgi"
            elif base.endswith('/nagios'):
                api_url = f"{base}/cgi-bin/statusjson.cgi"
            else:
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
                            "hint": "Verifica que el usuario y contraseña sean correctos y que la URL sea accesible desde el backend."
                        }
                    
                    data = await resp.json()
                    counts = data.get('data', {}).get('count', {})
                    
                # 2. Obtener lista de servicios con problemas
                async with session.get(f"{api_url}?query=servicelist", auth=auth, timeout=10) as resp:
                    problems = []
                    if resp.status == 200:
                        list_data = await resp.json()
                        data_content = list_data.get('data', {})
                        services_raw = data_content.get('servicelist', {})
                        
                        # Mapeo de bitmasks Nagios a códigos internos (0=OK, 1=WARN, 2=CRIT, 3=UNK)
                        # 2=OK, 4=WARN, 8=UNK, 16=CRIT
                        bitmask_map = {16: 2, 4: 1, 8: 3, 2: 0}
                        
                        if isinstance(services_raw, dict):
                            for h_name, s_dict in services_raw.items():
                                if isinstance(s_dict, dict):
                                    for s_desc, val in s_dict.items():
                                        # Si val es dict (detallado) o int (bitmask)
                                        status = val if isinstance(val, int) else val.get('status', 0)
                                        mapped_status = bitmask_map.get(status, 1 if status > 0 else 0)
                                        
                                        if mapped_status > 0:
                                            problems.append({
                                                "host": h_name,
                                                "service": s_desc,
                                                "status": mapped_status,
                                                "output": val.get('plugin_output', 'Ver Nagios para detalles') if isinstance(val, dict) else f"Status Bitmask: {status}"
                                            })
                        elif isinstance(services_raw, list):
                            for s_val in services_raw:
                                status = s_val.get('status', 0)
                                mapped_status = bitmask_map.get(status, 1 if status > 0 else 0)
                                if mapped_status > 0:
                                    problems.append({
                                        "host": s_val.get('host_name', 'Unknown'),
                                        "service": s_val.get('description', 'Unknown'),
                                        "status": mapped_status,
                                        "output": s_val.get('plugin_output', 'No info')
                                    })

                # Ordenar por severidad (CRIT primero)
                problems.sort(key=lambda x: x['status'], reverse=True)

                return {
                    "success": True,
                    "summary": {
                        "ok": counts.get('ok', 0),
                        "warning": counts.get('warning', 0),
                        "critical": counts.get('critical', 0),
                        "unknown": counts.get('unknown', 0),
                        "total": counts.get('all', 0)
                    },
                    "problems": problems[:50],
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
