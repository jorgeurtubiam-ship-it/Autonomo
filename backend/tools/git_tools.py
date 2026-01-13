"""
Git Operations Tools
Tools para operaciones con Git
"""

import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class GitStatusTool:
    """Tool para ver estado de Git"""
    
    name = "git_status"
    description = "Muestra el estado del repositorio Git (archivos modificados, staged, etc.)"
    category = "git"
    
    async def execute(self, path: str = ".") -> Dict[str, Any]:
        """
        Obtiene estado de Git
        
        Args:
            path: Ruta al repositorio
        
        Returns:
            Estado del repositorio
        """
        try:
            repo_path = Path(path).expanduser().resolve()
            
            # Ejecutar git status
            process = await asyncio.create_subprocess_exec(
                "git", "status", "--porcelain",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='replace')
                }
            
            # Parsear output
            status_lines = stdout.decode('utf-8').strip().split('\n')
            files = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }
            
            for line in status_lines:
                if not line:
                    continue
                    
                status = line[:2]
                filename = line[3:]
                
                if status == "??":
                    files["untracked"].append(filename)
                elif "M" in status:
                    files["modified"].append(filename)
                elif "A" in status:
                    files["added"].append(filename)
                elif "D" in status:
                    files["deleted"].append(filename)
            
            return {
                "success": True,
                "path": str(repo_path),
                "files": files,
                "total_changes": sum(len(v) for v in files.values())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo estado de Git: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta al repositorio Git (default: directorio actual)",
                        "default": "."
                    }
                }
            }
        }


class GitDiffTool:
    """Tool para ver diferencias en Git"""
    
    name = "git_diff"
    description = "Muestra las diferencias (cambios) en archivos del repositorio Git"
    category = "git"
    
    async def execute(self, path: str = ".", file: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene diff de Git
        
        Args:
            path: Ruta al repositorio
            file: Archivo específico (opcional)
        
        Returns:
            Diferencias
        """
        try:
            repo_path = Path(path).expanduser().resolve()
            
            cmd = ["git", "diff"]
            if file:
                cmd.append(file)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='replace')
                }
            
            return {
                "success": True,
                "path": str(repo_path),
                "file": file,
                "diff": stdout.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo diff: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta al repositorio Git",
                        "default": "."
                    },
                    "file": {
                        "type": "string",
                        "description": "Archivo específico para ver diff (opcional)"
                    }
                }
            }
        }


class GitCommitTool:
    """Tool para hacer commits en Git"""
    
    name = "git_commit"
    description = "Hace commit de los cambios staged en Git"
    category = "git"
    
    async def execute(
        self,
        message: str,
        path: str = ".",
        add_all: bool = False
    ) -> Dict[str, Any]:
        """
        Hace commit en Git
        
        Args:
            message: Mensaje del commit
            path: Ruta al repositorio
            add_all: Si hacer git add . antes del commit
        
        Returns:
            Resultado del commit
        """
        try:
            repo_path = Path(path).expanduser().resolve()
            
            # Git add si se solicita
            if add_all:
                process = await asyncio.create_subprocess_exec(
                    "git", "add", ".",
                    cwd=repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            
            # Git commit
            process = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", message,
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='replace')
                }
            
            return {
                "success": True,
                "path": str(repo_path),
                "message": message,
                "output": stdout.decode('utf-8', errors='replace')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error haciendo commit: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mensaje del commit"
                    },
                    "path": {
                        "type": "string",
                        "description": "Ruta al repositorio Git",
                        "default": "."
                    },
                    "add_all": {
                        "type": "boolean",
                        "description": "Si hacer 'git add .' antes del commit",
                        "default": False
                    }
                },
                "required": ["message"]
            }
        }


class GitLogTool:
    """Tool para ver historial de Git"""
    
    name = "git_log"
    description = "Muestra el historial de commits de Git"
    category = "git"
    
    async def execute(self, path: str = ".", limit: int = 10) -> Dict[str, Any]:
        """
        Obtiene log de Git
        
        Args:
            path: Ruta al repositorio
            limit: Número de commits a mostrar
        
        Returns:
            Historial de commits
        """
        try:
            repo_path = Path(path).expanduser().resolve()
            
            process = await asyncio.create_subprocess_exec(
                "git", "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode('utf-8', errors='replace')
                }
            
            # Parsear commits
            commits = []
            for line in stdout.decode('utf-8').strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
            
            return {
                "success": True,
                "path": str(repo_path),
                "commits": commits,
                "total": len(commits)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo log: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta al repositorio Git",
                        "default": "."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Número de commits a mostrar",
                        "default": 10
                    }
                }
            }
        }
