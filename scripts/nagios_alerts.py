#!/usr/bin/env python3
"""
Script para obtener alertas de Nagios
"""

import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re

# Configuración
NAGIOS_URL = "http://localhost:8080/nagios"
USERNAME = "nagiosadmin"
PASSWORD = "nagios@2025"

def get_nagios_alerts():
    """Obtiene alertas de Nagios"""
    
    # URL del status
    url = f"{NAGIOS_URL}/cgi-bin/status.cgi?host=all"
    
    try:
        # Hacer request con autenticación
        response = requests.get(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Conectado a Nagios exitosamente\n")
            
            # Parsear HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar tabla de servicios
            tables = soup.find_all('table', class_='status')
            
            if tables:
                print("📊 ALERTAS DE NAGIOS")
                print("=" * 80)
                
                # Contar estados
                ok_count = response.text.count('statusOK')
                warning_count = response.text.count('statusWARNING')
                critical_count = response.text.count('statusCRITICAL')
                unknown_count = response.text.count('statusUNKNOWN')
                
                print(f"\n📈 Resumen:")
                print(f"  🟢 OK:       {ok_count}")
                print(f"  🟡 WARNING:  {warning_count}")
                print(f"  🔴 CRITICAL: {critical_count}")
                print(f"  ⚪ UNKNOWN:  {unknown_count}")
                print()
                
                # Mostrar solo problemas
                if warning_count > 0 or critical_count > 0:
                    print("⚠️  PROBLEMAS DETECTADOS:")
                    print("-" * 80)
                    
                    # Buscar filas con problemas
                    rows = soup.find_all('tr', class_=re.compile('status(WARNING|CRITICAL)'))
                    
                    for row in rows[:10]:  # Mostrar primeros 10
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            host = cells[0].get_text(strip=True)
                            service = cells[1].get_text(strip=True)
                            status = cells[2].get_text(strip=True)
                            
                            status_icon = "🔴" if "CRITICAL" in row.get('class', []) else "🟡"
                            print(f"{status_icon} {host} - {service}")
                            print(f"   Estado: {status}")
                            print()
                else:
                    print("✅ ¡Todo está funcionando correctamente!")
                    
            else:
                print("⚠️  No se encontraron tablas de estado")
                print("Respuesta HTML recibida (primeros 500 caracteres):")
                print(response.text[:500])
                
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a Nagios")
        print("¿Está Nagios corriendo en http://localhost:8080?")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         VISOR DE ALERTAS DE NAGIOS                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    get_nagios_alerts()
