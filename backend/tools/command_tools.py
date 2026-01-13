"""
Command Execution Tools
Tools para ejecutar comandos shell y scripts
"""

import asyncio
import subprocess
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class ExecuteCommandParams(BaseModel):
    """Parámetros para execute_command"""
    command: str = Field(description="Comando a ejecutar")
    cwd: Optional[str] = Field(default=None, description="Directorio de trabajo")
    timeout: Optional[int] = Field(default=30, description="Timeout en segundos")


class ExecuteCommandTool:
    """Tool para ejecutar comandos shell"""
    
    name = "execute_command"
    description = "Ejecuta un comando shell. ⚠️ Puede ser peligroso - requiere aprobación para comandos destructivos."
    category = "command_execution"
    
    # Comandos bloqueados por seguridad
    BLOCKED_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=/dev/zero",
        ":(){ :|:& };:",  # Fork bomb
        "chmod -R 777 /",
    ]
    
    async def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Ejecuta un comando shell
        
        Args:
            command: Comando a ejecutar
            cwd: Directorio de trabajo (opcional)
            timeout: Timeout en segundos
        
        Returns:
            Resultado de la ejecución
        """
        try:
            # Verificar comandos bloqueados
            for blocked in self.BLOCKED_COMMANDS:
                if blocked in command:
                    return {
                        "success": False,
                        "error": f"Comando bloqueado por seguridad: {blocked}",
                        "blocked": True
                    }
            
            # Preparar directorio de trabajo
            work_dir = None
            if cwd:
                work_dir = Path(cwd).expanduser().resolve()
                if not work_dir.exists():
                    return {
                        "success": False,
                        "error": f"Directorio no encontrado: {cwd}"
                    }
            
            # Ejecutar comando
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Comando excedió timeout de {timeout}s",
                    "timeout": True
                }
            
            return {
                "success": process.returncode == 0,
                "command": command,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "cwd": str(work_dir) if work_dir else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error ejecutando comando: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Comando shell a ejecutar"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Directorio de trabajo (opcional)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout en segundos (default: 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        }


class RunScriptParams(BaseModel):
    """Parámetros para run_script"""
    script_path: str = Field(description="Ruta al script")
    args: Optional[list] = Field(default=None, description="Argumentos del script")
    interpreter: Optional[str] = Field(default=None, description="Intérprete (python, bash, node, etc.)")


class RunScriptTool:
    """Tool para ejecutar scripts"""
    
    name = "run_script"
    description = "Ejecuta un script (Python, Bash, Node.js, etc.)"
    category = "command_execution"
    
    async def execute(
        self,
        script_path: str,
        args: Optional[list] = None,
        interpreter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un script
        
        Args:
            script_path: Ruta al script
            args: Argumentos del script
            interpreter: Intérprete a usar
        
        Returns:
            Resultado de la ejecución
        """
        try:
            script = Path(script_path).expanduser().resolve()
            
            if not script.exists():
                return {
                    "success": False,
                    "error": f"Script no encontrado: {script_path}"
                }
            
            # Detectar intérprete si no se especifica
            if not interpreter:
                ext = script.suffix.lower()
                interpreters = {
                    '.py': 'python',
                    '.sh': 'bash',
                    '.js': 'node',
                    '.rb': 'ruby',
                    '.pl': 'perl'
                }
                interpreter = interpreters.get(ext, 'bash')
            
            # Construir comando
            cmd = [interpreter, str(script)]
            if args:
                cmd.extend(args)
            
            # Ejecutar
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "script": str(script),
                "interpreter": interpreter,
                "args": args or [],
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error ejecutando script: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Ruta al script a ejecutar"
                    },
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Argumentos del script (opcional)"
                    },
                    "interpreter": {
                        "type": "string",
                        "description": "Intérprete a usar (python, bash, node, etc.). Auto-detecta si no se especifica"
                    }
                },
                "required": ["script_path"]
            }
        }


class InstallPackageParams(BaseModel):
    """Parámetros para install_package"""
    package: str = Field(description="Nombre del paquete")
    manager: str = Field(default="pip", description="Gestor de paquetes (pip, npm, apt, etc.)")


class InstallPackageTool:
    """Tool para instalar paquetes"""
    
    name = "install_package"
    description = "Instala un paquete usando un gestor de paquetes (pip, npm, apt, brew, etc.)"
    category = "command_execution"
    
    async def execute(
        self,
        package: str,
        manager: str = "pip"
    ) -> Dict[str, Any]:
        """
        Instala un paquete
        
        Args:
            package: Nombre del paquete
            manager: Gestor de paquetes
        
        Returns:
            Resultado de la instalación
        """
        try:
            # Comandos de instalación por gestor
            install_commands = {
                "pip": ["pip", "install", package],
                "pip3": ["pip3", "install", package],
                "npm": ["npm", "install", package],
                "yarn": ["yarn", "add", package],
                "apt": ["sudo", "apt-get", "install", "-y", package],
                "brew": ["brew", "install", package],
                "cargo": ["cargo", "install", package]
            }
            
            if manager not in install_commands:
                return {
                    "success": False,
                    "error": f"Gestor de paquetes no soportado: {manager}"
                }
            
            cmd = install_commands[manager]
            
            # Ejecutar instalación
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "package": package,
                "manager": manager,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error instalando paquete: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Nombre del paquete a instalar"
                    },
                    "manager": {
                        "type": "string",
                        "description": "Gestor de paquetes (pip, npm, apt, brew, etc.)",
                        "default": "pip",
                        "enum": ["pip", "pip3", "npm", "yarn", "apt", "brew", "cargo"]
                    }
                },
                "required": ["package"]
            }
        }
