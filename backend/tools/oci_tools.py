"""
OCI Tools - Herramientas para interactuar con Oracle Cloud Infrastructure (OCI)
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class OCIListInstancesParams(BaseModel):
    """Parámetros para oci_list_instances"""
    compartment_id: str = Field(..., description="ID del compartimento (OCID).")
    region: Optional[str] = Field(default=None, description="Región de OCI (ej: us-ashburn-1).")

class OCITool:
    """Tool para que el agente gestione recursos en Oracle Cloud (OCI)"""
    
    name = "oci_list_instances"
    description = "Lista las instancias de cómputo en un compartimento de OCI. Úsalo para ver qué servidores tienes en Oracle Cloud."
    category = "cloud"

    async def execute(self, compartment_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta comando OCI CLI para listar instancias
        """
        cmd = ["oci", "compute", "instance", "list", "--compartment-id", compartment_id, "--output", "json"]
        if region:
            cmd.extend(["--region", region])
            
        try:
            logger.info(f"OCITool: Ejecutando {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                # OCI CLI retorna una lista en la raíz o bajo 'data'
                instances = data.get("data", data) if isinstance(data, dict) else data
                
                formatted_instances = []
                for inst in instances:
                    formatted_instances.append({
                        "id": inst.get("id"),
                        "display_name": inst.get("display-name"),
                        "shape": inst.get("shape"),
                        "lifecycle_state": inst.get("lifecycle-state"),
                        "availability_domain": inst.get("availability-domain"),
                        "time_created": inst.get("time-created")
                    })
                    
                return {
                    "success": True,
                    "count": len(formatted_instances),
                    "instances": formatted_instances
                }
            else:
                error_msg = stderr.decode()
                logger.error(f"Error en OCI CLI: {error_msg}")
                return {
                    "success": False, 
                    "error": f"Error ejecutando OCI CLI: {error_msg}",
                    "instruction": "Asegúrate de tener instalada y configurada la OCI CLI ('oci setup config')."
                }
                
        except Exception as e:
            logger.error(f"Error en OCITool: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "compartment_id": {
                        "type": "string",
                        "description": "OCID del compartimento."
                    },
                    "region": {
                        "type": "string",
                        "description": "Región opcional."
                    }
                },
                "required": ["compartment_id"]
            }
        }
