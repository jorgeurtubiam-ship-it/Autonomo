"""
HTTP Request Tool - Para llamar APIs externas
"""

import aiohttp
import json
from typing import Dict, Any, Optional


class HttpRequestTool:
    """Tool para hacer peticiones HTTP a APIs externas"""
    
    name = "http_request"
    description = "Realiza peticiones HTTP a APIs externas. Soporta GET, POST, PUT, DELETE. Útil para consultar servicios web, APIs REST, y endpoints externos como Nagios, Grafana, etc."
    category = "http"
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna la definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL completa del endpoint (ej: http://localhost:8080/nagios/cgi-bin/statusjson.cgi?query=servicecount)"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "Método HTTP a usar (default: GET)",
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "Headers HTTP opcionales como dict (ej: {'Content-Type': 'application/json'})",
                        "additionalProperties": {"type": "string"}
                    },
                    "body": {
                        "type": "string",
                        "description": "Cuerpo de la petición para POST/PUT (string JSON)"
                    },
                    "auth_user": {
                        "type": "string",
                        "description": "Usuario para autenticación básica HTTP"
                    },
                    "auth_pass": {
                        "type": "string",
                        "description": "Contraseña para autenticación básica HTTP"
                    },
                    "verify_ssl": {
                        "type": "boolean",
                        "description": "Si verificar certificados SSL (usar false para desarrollo local)",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        auth_user: Optional[str] = None,
        auth_pass: Optional[str] = None,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecuta una petición HTTP
        
        Args:
            url: URL completa del endpoint
            method: Método HTTP (GET, POST, PUT, DELETE, PATCH)
            headers: Headers HTTP opcionales
            body: Cuerpo de la petición para POST/PUT
            auth_user: Usuario para autenticación básica
            auth_pass: Contraseña para autenticación básica
            verify_ssl: Si verificar certificados SSL
        
        Returns:
            Dict con success, status_code, headers, y body de la respuesta
        """
        method = method.upper()
        
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            return {
                "success": False,
                "error": f"Método HTTP inválido: {method}",
                "valid_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]
            }
        
        # Preparar autenticación
        auth = None
        if auth_user and auth_pass:
            auth = aiohttp.BasicAuth(auth_user, auth_pass)
        
        # Preparar headers
        request_headers = headers or {}
        
        try:
            # Crear sesión con configuración SSL
            connector = aiohttp.TCPConnector(ssl=verify_ssl)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Preparar kwargs
                kwargs = {
                    "headers": request_headers,
                    "auth": auth,
                    "timeout": aiohttp.ClientTimeout(total=30)
                }
                
                # Agregar body si es POST/PUT/PATCH
                if method in ["POST", "PUT", "PATCH"] and body:
                    kwargs["data"] = body
                
                # Hacer request
                async with session.request(method, url, **kwargs) as response:
                    # Leer respuesta
                    try:
                        response_text = await response.text()
                        
                        # Intentar parsear como JSON
                        try:
                            response_body = json.loads(response_text)
                        except json.JSONDecodeError:
                            # Si no es JSON, retornar texto (limitado a 1000 chars)
                            response_body = response_text[:1000]
                            if len(response_text) > 1000:
                                response_body += "... (truncado)"
                        
                    except Exception as e:
                        response_body = f"Error leyendo respuesta: {str(e)}"
                    
                    # Construir respuesta
                    result = {
                        "success": 200 <= response.status < 300,
                        "status_code": response.status,
                        "status_text": response.reason,
                        "url": str(response.url),
                        "method": method,
                        "body": response_body,
                        "headers": dict(response.headers)
                    }
                    
                    return result
                    
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Error de conexión: {str(e)}",
                "url": url,
                "method": method
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "url": url,
                "method": method
            }
