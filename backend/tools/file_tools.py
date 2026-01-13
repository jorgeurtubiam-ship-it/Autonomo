"""
File Operations Tools
Tools para gestión de archivos y directorios
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import glob


class ReadFileParams(BaseModel):
    """Parámetros para read_file"""
    path: str = Field(description="Ruta al archivo a leer")


class ReadFileTool:
    """Tool para leer archivos"""
    
    name = "read_file"
    description = "Lee el contenido de un archivo. Retorna el contenido completo del archivo."
    category = "file_operations"
    
    async def execute(self, path: str) -> Dict[str, Any]:
        """
        Lee un archivo
        
        Args:
            path: Ruta al archivo
        
        Returns:
            Contenido del archivo
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Archivo no encontrado: {path}"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "error": f"La ruta no es un archivo: {path}"
                }
            
            # Leer archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "El archivo no es texto plano (posiblemente binario)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error leyendo archivo: {str(e)}"
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
                        "description": "Ruta al archivo a leer (absoluta o relativa)"
                    }
                },
                "required": ["path"]
            }
        }


class WriteFileParams(BaseModel):
    """Parámetros para write_file"""
    path: str = Field(description="Ruta donde crear/escribir el archivo")
    content: str = Field(description="Contenido a escribir en el archivo")


class WriteFileTool:
    """Tool para escribir archivos"""
    
    name = "write_file"
    description = "Crea un nuevo archivo o sobrescribe uno existente con el contenido proporcionado."
    category = "file_operations"
    
    async def execute(self, path: str, content: str) -> Dict[str, Any]:
        """
        Escribe un archivo
        
        Args:
            path: Ruta al archivo
            content: Contenido a escribir
        
        Returns:
            Resultado de la operación
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Crear directorios padre si no existen
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content),
                "lines": len(content.splitlines()),
                "message": f"Archivo {'creado' if not file_path.exists() else 'actualizado'} exitosamente"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error escribiendo archivo: {str(e)}"
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
                        "description": "Ruta donde crear/escribir el archivo"
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido a escribir en el archivo"
                    }
                },
                "required": ["path", "content"]
            }
        }


class ListDirectoryParams(BaseModel):
    """Parámetros para list_directory"""
    path: str = Field(default=".", description="Ruta al directorio a listar")


class ListDirectoryTool:
    """Tool para listar contenido de directorios"""
    
    name = "list_directory"
    description = "Lista el contenido de un directorio. Muestra archivos y subdirectorios con sus tamaños."
    category = "file_operations"
    
    async def execute(self, path: str = ".") -> Dict[str, Any]:
        """
        Lista un directorio
        
        Args:
            path: Ruta al directorio
        
        Returns:
            Lista de archivos y directorios
        """
        try:
            dir_path = Path(path).expanduser().resolve()
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directorio no encontrado: {path}"
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "error": f"La ruta no es un directorio: {path}"
                }
            
            # Listar contenido
            items = []
            for item in sorted(dir_path.iterdir()):
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                }
                
                if item.is_file():
                    item_info["size"] = item.stat().st_size
                
                items.append(item_info)
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "total": len(items),
                "files": len([i for i in items if i["type"] == "file"]),
                "directories": len([i for i in items if i["type"] == "directory"])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listando directorio: {str(e)}"
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
                        "description": "Ruta al directorio a listar (por defecto: directorio actual)",
                        "default": "."
                    }
                }
            }
        }


class SearchFilesParams(BaseModel):
    """Parámetros para search_files"""
    pattern: str = Field(description="Patrón de búsqueda (glob pattern)")
    path: str = Field(default=".", description="Directorio donde buscar")


class SearchFilesTool:
    """Tool para buscar archivos"""
    
    name = "search_files"
    description = "Busca archivos por patrón (glob). Ejemplos: '*.py', '**/*.js', 'test_*.py'"
    category = "file_operations"
    
    async def execute(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """
        Busca archivos
        
        Args:
            pattern: Patrón de búsqueda (glob)
            path: Directorio donde buscar
        
        Returns:
            Lista de archivos encontrados
        """
        try:
            search_path = Path(path).expanduser().resolve()
            
            if not search_path.exists():
                return {
                    "success": False,
                    "error": f"Directorio no encontrado: {path}"
                }
            
            # Buscar archivos
            if "**" in pattern:
                # Búsqueda recursiva
                matches = list(search_path.glob(pattern))
            else:
                # Búsqueda en directorio actual
                matches = list(search_path.glob(pattern))
            
            files = []
            for match in matches:
                if match.is_file():
                    files.append({
                        "name": match.name,
                        "path": str(match),
                        "size": match.stat().st_size
                    })
            
            return {
                "success": True,
                "pattern": pattern,
                "search_path": str(search_path),
                "files": files,
                "total": len(files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error buscando archivos: {str(e)}"
            }
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Patrón de búsqueda glob (ej: '*.py', '**/*.js')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directorio donde buscar (por defecto: directorio actual)",
                        "default": "."
                    }
                },
                "required": ["pattern"]
            }
        }


class DeleteFileParams(BaseModel):
    """Parámetros para delete_file"""
    path: str = Field(description="Ruta al archivo o directorio a eliminar")


class DeleteFileTool:
    """Tool para eliminar archivos y directorios"""
    
    name = "delete_file"
    description = "Elimina un archivo o directorio. ⚠️ ACCIÓN DESTRUCTIVA - requiere confirmación."
    category = "file_operations"
    
    async def execute(self, path: str) -> Dict[str, Any]:
        """
        Elimina un archivo o directorio
        
        Args:
            path: Ruta a eliminar
        
        Returns:
            Resultado de la operación
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Ruta no encontrada: {path}"
                }
            
            if file_path.is_file():
                file_path.unlink()
                return {
                    "success": True,
                    "path": str(file_path),
                    "type": "file",
                    "message": "Archivo eliminado exitosamente"
                }
            elif file_path.is_dir():
                shutil.rmtree(file_path)
                return {
                    "success": True,
                    "path": str(file_path),
                    "type": "directory",
                    "message": "Directorio eliminado exitosamente"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error eliminando: {str(e)}"
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
                        "description": "Ruta al archivo o directorio a eliminar"
                    }
                },
                "required": ["path"]
            }
        }


class GetFileInfoParams(BaseModel):
    """Parámetros para get_file_info"""
    path: str = Field(description="Ruta al archivo")


class GetFileInfoTool:
    """Tool para obtener información de archivos"""
    
    name = "get_file_info"
    description = "Obtiene información detallada de un archivo (tamaño, fecha modificación, permisos, etc.)"
    category = "file_operations"
    
    async def execute(self, path: str) -> Dict[str, Any]:
        """
        Obtiene info de un archivo
        
        Args:
            path: Ruta al archivo
        
        Returns:
            Información del archivo
        """
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Archivo no encontrado: {path}"
                }
            
            stat = file_path.stat()
            
            return {
                "success": True,
                "path": str(file_path),
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:],
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK),
                "is_executable": os.access(file_path, os.X_OK)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error obteniendo info: {str(e)}"
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
                        "description": "Ruta al archivo"
                    }
                },
                "required": ["path"]
            }
        }
