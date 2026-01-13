"""
Tests para Command Tools
"""

import pytest
from backend.tools.command_tools import ExecuteCommandTool


@pytest.mark.asyncio
async def test_execute_simple_command():
    """Test de ejecución de comando simple"""
    cmd_tool = ExecuteCommandTool()
    
    result = await cmd_tool.execute(command="echo 'Hello Test'")
    
    assert result["success"] == True
    assert "Hello Test" in result["stdout"]
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_blocked_command():
    """Test de comando bloqueado"""
    cmd_tool = ExecuteCommandTool()
    
    result = await cmd_tool.execute(command="rm -rf /")
    
    assert result["success"] == False
    assert result.get("blocked") == True


@pytest.mark.asyncio
async def test_command_with_cwd():
    """Test de comando con directorio de trabajo"""
    cmd_tool = ExecuteCommandTool()
    
    result = await cmd_tool.execute(
        command="pwd",
        cwd="/tmp"
    )
    
    assert result["success"] == True
    assert "/tmp" in result["stdout"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
