"""
AWS Tools - Herramientas para interactuar con Amazon Web Services (AWS)
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AWSListInstancesTool:
    """Tool para que el agente gestione recursos en AWS"""
    
    name = "aws_list_instances"
    description = "Lista las instancias EC2 en AWS. Úsalo para ver qué servidores tienes en Amazon Web Services. NO lo confundas con OCI."
    category = "cloud"

    async def execute(self, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta comando AWS CLI para listar instancias
        """
        cmd = ["aws", "ec2", "describe-instances", "--output", "json"]
        if region:
            cmd.extend(["--region", region])
            
        try:
            logger.info(f"AWSTool: Ejecutando {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                
                formatted_instances = []
                for reservation in data.get("Reservations", []):
                    for inst in reservation.get("Instances", []):
                        # Extraer Name del tag si existe
                        name = "N/A"
                        for tag in inst.get("Tags", []):
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break
                                
                        formatted_instances.append({
                            "InstanceId": inst.get("InstanceId"),
                            "InstanceType": inst.get("InstanceType"),
                            "State": inst.get("State", {}).get("Name"),
                            "PublicIpAddress": inst.get("PublicIpAddress", "N/A"),
                            "Name": name,
                            "LaunchTime": inst.get("LaunchTime")
                        })
                        
                return {
                    "success": True,
                    "count": len(formatted_instances),
                    "instances": formatted_instances
                }
            else:
                error_msg = stderr.decode()
                logger.error(f"Error en AWS CLI: {error_msg}")
                return {
                    "success": False, 
                    "error": f"Error ejecutando AWS CLI: {error_msg}",
                    "instruction": "Asegúrate de tener instalada y configurada la AWS CLI ('aws configure')."
                }
                
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Comando 'aws' no encontrado.",
                "instruction": "Instala la AWS CLI e intenta nuevamente."
            }
        except Exception as e:
            logger.error(f"Error en AWSTool: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Región de AWS (ej: us-east-1). Opcional."
                    }
                }
            }
        }
