#!/usr/bin/env python3
"""
Visor de Alertas de Nagios usando JSON API
Usa los endpoints correctos de Nagios JSON
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# Configuración
NAGIOS_CONFIG = {
    "base_url": "http://localhost:8080/nagios/cgi-bin/statusjson.cgi",
    "user": "nagiosadmin",
    "pass": "nagios@2025"
}

def get_nagios_data(query_type):
    """Obtiene datos de Nagios JSON API"""
    url = f"{NAGIOS_CONFIG['base_url']}?query={query_type}"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(NAGIOS_CONFIG['user'], NAGIOS_CONFIG['pass']),
        timeout=10
    )
    
    if response.status_code == 200:
        return response.json()
    return None


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║      ALERTAS DE NAGIOS - JSON API                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 1. Obtener conteo de servicios
        print("🔄 Obteniendo estado de servicios...")
        service_count = get_nagios_data("servicecount")
        
        if service_count and 'data' in service_count:
            counts = service_count['data']['count']
            
            print("\n📊 RESUMEN DE SERVICIOS")
            print("=" * 80)
            print(f"  🟢 OK:       {counts.get('ok', 0)}")
            print(f"  🟡 WARNING:  {counts.get('warning', 0)}")
            print(f"  🔴 CRITICAL: {counts.get('critical', 0)}")
            print(f"  ⚪ UNKNOWN:  {counts.get('unknown', 0)}")
            print(f"  ⏸️  PENDING:  {counts.get('pending', 0)}")
            print(f"  📊 TOTAL:    {counts.get('all', 0)}")
        
        # 2. Obtener lista de servicios con problemas
        print("\n🔄 Obteniendo lista de servicios...")
        service_list = get_nagios_data("servicelist")
        
        if service_list and 'data' in service_list:
            services = service_list['data']['servicelist']
            
            # Filtrar solo problemas
            problems = [s for s in services.values() 
                       if s.get('status', 0) > 0]
            
            if problems:
                print(f"\n⚠️  PROBLEMAS DETECTADOS ({len(problems)}):")
                print("-" * 80)
                
                # Ordenar por severidad
                problems.sort(key=lambda x: x.get('status', 0), reverse=True)
                
                for service in problems[:20]:  # Mostrar primeros 20
                    status_map = {
                        0: "🟢 OK",
                        1: "🟡 WARNING",
                        2: "🔴 CRITICAL",
                        3: "⚪ UNKNOWN"
                    }
                    
                    status = service.get('status', 3)
                    status_icon = status_map.get(status, "❓")
                    
                    host = service.get('host_name', 'Unknown')
                    svc_name = service.get('description', 'Unknown')
                    output = service.get('plugin_output', 'No info')
                    last_check = service.get('last_check', 0)
                    
                    print(f"\n{status_icon} {host} → {svc_name}")
                    print(f"   💬 {output[:100]}")
                    if service.get('acknowledged', False):
                        print(f"   ✅ Reconocido")
            else:
                print("\n✅ ¡No hay problemas! Todo está funcionando correctamente.")
        
        # 3. Obtener estado de hosts
        print("\n🔄 Obteniendo estado de hosts...")
        host_count = get_nagios_data("hostcount")
        
        if host_count and 'data' in host_count:
            counts = host_count['data']['count']
            
            print("\n🖥️  RESUMEN DE HOSTS")
            print("=" * 80)
            print(f"  🟢 UP:          {counts.get('up', 0)}")
            print(f"  🔴 DOWN:        {counts.get('down', 0)}")
            print(f"  🟡 UNREACHABLE: {counts.get('unreachable', 0)}")
            print(f"  ⏸️  PENDING:     {counts.get('pending', 0)}")
            print(f"  📊 TOTAL:       {counts.get('all', 0)}")
        
        # 4. Mostrar hosts con problemas
        host_list = get_nagios_data("hostlist")
        
        if host_list and 'data' in host_list:
            hosts = host_list['data']['hostlist']
            
            host_problems = [h for h in hosts.values() 
                           if h.get('status', 0) > 0]
            
            if host_problems:
                print(f"\n⚠️  HOSTS CON PROBLEMAS ({len(host_problems)}):")
                print("-" * 80)
                
                for host in host_problems:
                    status_map = {
                        0: "🟢 UP",
                        1: "🔴 DOWN",
                        2: "🟡 UNREACHABLE"
                    }
                    
                    status = host.get('status', 0)
                    status_icon = status_map.get(status, "❓")
                    
                    name = host.get('name', 'Unknown')
                    output = host.get('plugin_output', 'No info')
                    
                    print(f"\n{status_icon} {name}")
                    print(f"   💬 {output[:100]}")
        
        print("\n" + "=" * 80)
        print("💡 Para más detalles: http://localhost:8080/nagios/")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a Nagios")
        print(f"   URL: {NAGIOS_CONFIG['base_url']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
