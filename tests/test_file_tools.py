"""
Tests para File Tools
"""

import pytest
import asyncio
from pathlib import Path
from backend.tools.file_tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    SearchFilesTool,
    GetFileInfoTool
)


@pytest.mark.asyncio
async def test_write_and_read_file():
    """Test de escritura y lectura de archivos"""
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()
    
    # Escribir archivo
    test_content = "Este es un test\nCon múltiples líneas"
    result = await write_tool.execute(
        path="test_file.txt",
        content=test_content
    )
    
    assert result["success"] == True
    assert "test_file.txt" in result["path"]
    
    # Leer archivo
    result = await read_tool.execute(path="test_file.txt")
    
    assert result["success"] == True
    assert result["content"] == test_content
    assert result["lines"] == 2
    
    # Limpiar
    Path("test_file.txt").unlink()


@pytest.mark.asyncio
async def test_list_directory():
    """Test de listado de directorios"""
    list_tool = ListDirectoryTool()
    
    result = await list_tool.execute(path=".")
    
    assert result["success"] == True
    assert "items" in result
    assert result["total"] > 0
    assert isinstance(result["items"], list)


@pytest.mark.asyncio
async def test_search_files():
    """Test de búsqueda de archivos"""
    search_tool = SearchFilesTool()
    
    # Buscar archivos Python
    result = await search_tool.execute(pattern="*.py", path="backend/tools")
    
    assert result["success"] == True
    assert "files" in result
    assert len(result["files"]) > 0


@pytest.mark.asyncio
async def test_get_file_info():
    """Test de info de archivos"""
    # Crear archivo temporal
    test_file = Path("test_info.txt")
    test_file.write_text("test")
    
    info_tool = GetFileInfoTool()
    result = await info_tool.execute(path="test_info.txt")
    
    assert result["success"] == True
    assert result["type"] == "file"
    assert result["size"] > 0
    
    # Limpiar
    test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
