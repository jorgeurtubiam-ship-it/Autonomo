"""
Tests para BrowserTool
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from tools.browser_tool import BrowserTool


@pytest.fixture
async def browser_tool():
    """Fixture que crea una instancia de BrowserTool"""
    tool = BrowserTool()
    yield tool
    # Cleanup: cerrar navegador después de cada test
    await tool._close_browser()


@pytest.mark.asyncio
async def test_browser_tool_navigate():
    """Test de navegación básica"""
    tool = BrowserTool()
    
    result = await tool.execute(
        action="navigate",
        url="https://example.com"
    )
    
    assert result["success"] is True
    assert "example.com" in result["url"].lower()
    assert result["title"]
    assert result["status"] == 200
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_screenshot():
    """Test de captura de screenshot"""
    tool = BrowserTool()
    
    # Primero navegar
    await tool.execute(action="navigate", url="https://example.com")
    
    # Tomar screenshot
    result = await tool.execute(action="screenshot")
    
    assert result["success"] is True
    assert "screenshot_path" in result
    assert Path(result["screenshot_path"]).exists()
    assert result["filename"].endswith(".png")
    
    # Cleanup
    Path(result["screenshot_path"]).unlink()  # Eliminar screenshot de prueba
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_extract():
    """Test de extracción de contenido"""
    tool = BrowserTool()
    
    # Navegar a example.com
    await tool.execute(action="navigate", url="https://example.com")
    
    # Extraer información general
    result = await tool.execute(action="extract")
    
    assert result["success"] is True
    assert result["title"]
    assert result["url"]
    assert result["text"]
    assert "Example Domain" in result["text"]
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_extract_with_selector():
    """Test de extracción con selector CSS"""
    tool = BrowserTool()
    
    await tool.execute(action="navigate", url="https://example.com")
    
    # Extraer texto del h1
    result = await tool.execute(
        action="extract",
        selector="h1"
    )
    
    assert result["success"] is True
    assert "Example Domain" in result["text"]
    assert result["selector"] == "h1"
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_wait():
    """Test de espera por elemento"""
    tool = BrowserTool()
    
    await tool.execute(action="navigate", url="https://example.com")
    
    # Esperar por el h1
    result = await tool.execute(
        action="wait",
        selector="h1",
        timeout=5000
    )
    
    assert result["success"] is True
    assert result["selector"] == "h1"
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_scroll():
    """Test de scroll"""
    tool = BrowserTool()
    
    await tool.execute(action="navigate", url="https://example.com")
    
    result = await tool.execute(action="scroll")
    
    assert result["success"] is True
    assert "Scroll realizado" in result["message"]
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_back_forward():
    """Test de navegación hacia atrás y adelante"""
    tool = BrowserTool()
    
    # Navegar a dos páginas
    await tool.execute(action="navigate", url="https://example.com")
    await tool.execute(action="navigate", url="https://www.iana.org")
    
    # Ir hacia atrás
    result_back = await tool.execute(action="back")
    assert result_back["success"] is True
    assert "example.com" in result_back["url"]
    
    # Ir hacia adelante
    result_forward = await tool.execute(action="forward")
    assert result_forward["success"] is True
    assert "iana.org" in result_forward["url"]
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_error_handling():
    """Test de manejo de errores"""
    tool = BrowserTool()
    
    # Intentar navegar sin URL
    result = await tool.execute(action="navigate")
    assert result["success"] is False
    assert "error" in result
    
    # Intentar acción desconocida
    result = await tool.execute(action="invalid_action")
    assert result["success"] is False
    assert "desconocida" in result["error"].lower()
    
    await tool.execute(action="close")


@pytest.mark.asyncio
async def test_browser_tool_multiple_actions():
    """Test de múltiples acciones en secuencia"""
    tool = BrowserTool()
    
    # Secuencia de acciones
    r1 = await tool.execute(action="navigate", url="https://example.com")
    assert r1["success"] is True
    
    r2 = await tool.execute(action="extract")
    assert r2["success"] is True
    
    r3 = await tool.execute(action="screenshot")
    assert r3["success"] is True
    
    r4 = await tool.execute(action="scroll")
    assert r4["success"] is True
    
    # Cleanup
    if r3["success"]:
        Path(r3["screenshot_path"]).unlink()
    
    await tool.execute(action="close")


def test_browser_tool_definition():
    """Test de definición del tool"""
    tool = BrowserTool()
    definition = tool.get_definition()
    
    assert definition["name"] == "browser"
    assert definition["description"]
    assert "parameters" in definition
    assert "action" in definition["parameters"]["properties"]
    
    # Verificar que todas las acciones estén en el enum
    actions = definition["parameters"]["properties"]["action"]["enum"]
    expected_actions = ["navigate", "screenshot", "extract", "click", "type", "scroll", "wait", "back", "forward", "close"]
    assert set(actions) == set(expected_actions)


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "-s"])
