import sys
import os

# Agregar /Users/lordzero1/IA_LoRdZeRo/auto/backend al path para importar tools y agent
sys.path.append("/Users/lordzero1/IA_LoRdZeRo/auto/backend")

from tools import get_all_tools

def verify_registration():
    tools = get_all_tools()
    tool_names = [t.name for t in tools]
    
    expected_tools = [
        "zabbix_get_alerts",
        "rundeck_run_job",
        "rundeck_list_jobs",
        "analyze_cloud_resources",
        "oci_list_instances",
        "dremio_query",
        "dremio_list_catalog",
        "checkmk_get_alerts",
        "checkmk_list_hosts",
        "aws_list_instances"
    ]
    
    print("\n--- Verificación de Registro de Herramientas ---")
    all_present = True
    for tool_name in expected_tools:
        if tool_name in tool_names:
            print(f"✅ {tool_name}: Registrada correctamente")
        else:
            print(f"❌ {tool_name}: NO encontrada")
            all_present = False
            
    if all_present:
        print("\n✨ Todas las nuevas herramientas están registradas exitosamente.")
    else:
        print("\n⚠️ Faltan algunas herramientas en el registro.")
        sys.exit(1)

if __name__ == "__main__":
    verify_registration()
