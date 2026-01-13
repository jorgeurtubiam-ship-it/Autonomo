"""
Analysis Tools - Herramientas para analizar infraestructura y costos
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CloudResourceAnalysisParams(BaseModel):
    """Parámetros para analyze_cloud_resources"""
    provider: str = Field(..., description="Proveedor de nube (aws, oci, gcp, azure).")
    resources_json: str = Field(..., description="Datos de los recursos en formato JSON (ej. salida de 'aws ec2 describe-instances').")

class InfrastructureAnalysisTool:
    """Tool para analizar datos de infraestructura y sugerir optimizaciones"""
    
    name = "analyze_cloud_resources"
    description = "Analiza datos crudos de recursos de nube (como listas de instancias o métricas de uso) y genera recomendaciones de optimización de costos (Right-sizing) y rendimiento."
    category = "analysis"

    async def execute(self, provider: str, resources_json: str) -> Dict[str, Any]:
        """
        Analiza recursos y genera recomendaciones
        """
        import json
        try:
            data = json.loads(resources_json)
            recommendations = []
            summary = {"total_resources": 0, "optimizable": 0}
            
            if provider.lower() == "aws":
                # Lógica simplificada de análisis para AWS EC2
                instances = []
                if isinstance(data, dict):
                    if "Reservations" in data:
                        for res in data["Reservations"]:
                            instances.extend(res.get("Instances", []))
                    else:
                        instances = data.get("Instances", [])
                elif isinstance(data, list):
                    instances = data
                
                summary["total_resources"] = len(instances)
                
                for inst in instances:
                    inst_id = inst.get("InstanceId")
                    inst_type = inst.get("InstanceType")
                    state = inst.get("State", {}).get("Name")
                    
                    # Recomendación: Instancias apagadas que podrían ser eliminadas
                    if state == "stopped":
                        recommendations.append({
                            "resource_id": inst_id,
                            "type": inst_type,
                            "issue": "Instancia detenida",
                            "recommendation": "Considerar eliminación si no se planea reactivar para ahorrar en almacenamiento EBS.",
                            "severity": "Low"
                        })
                        summary["optimizable"] += 1
                    
                    # Recomendación: Tipos de instancia antiguos
                    elif inst_type.startswith(("t2.", "m4.", "c4.")):
                        gen = inst_type.split('.')[0]
                        modern_equiv = inst_type.replace(gen, gen.replace('2', '3').replace('4', '5'))
                        recommendations.append({
                            "resource_id": inst_id,
                            "type": inst_type,
                            "issue": f"Generación antigua ({gen})",
                            "recommendation": f"Migrar a familia {modern_equiv} para mejor rendimiento/precio.",
                            "severity": "Medium"
                        })
                        summary["optimizable"] += 1

            elif provider.lower() == "oci":
                # Lógica para OCI Compute
                instances = data if isinstance(data, list) else data.get("instances", [])
                summary["total_resources"] = len(instances)
                
                for inst in instances:
                    # Ejemplo OCI (shape)
                    shape = inst.get("shape")
                    state = inst.get("lifecycleState")
                    
                    if state == "STOPPED":
                        recommendations.append({
                            "resource_id": inst.get("id"),
                            "type": shape,
                            "issue": "Instancia detenida",
                            "recommendation": "Terminar instancia si el volumen de arranque no es necesario.",
                            "severity": "Low"
                        })
                        summary["optimizable"] += 1

            return {
                "success": True,
                "provider": provider,
                "summary": summary,
                "recommendations": recommendations,
                "message": f"Se analizaron {summary['total_resources']} recursos y se encontraron {summary['optimizable']} oportunidades de optimización."
            }
            
        except Exception as e:
            logger.error(f"Error en InfrastructureAnalysisTool: {e}")
            return {"success": False, "error": f"Error parseando datos: {str(e)}"}

    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["aws", "oci", "gcp", "azure"],
                        "description": "Proveedor de la nube."
                    },
                    "resources_json": {
                        "type": "string",
                        "description": "El JSON con los datos de los recursos a analizar."
                    }
                },
                "required": ["provider", "resources_json"]
            }
        }
