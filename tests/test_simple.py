"""
Test simple sin dependencias externas
Verifica la estructura básica de los tools
"""

import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.tools.file_tools import ReadFileTool, WriteFileTool
from backend.tools.command_tools import ExecuteCommandTool


def test_tool_definitions():
    """Test de definiciones de tools"""
    
    print("Testing tool definitions...")
    
    # File tools
    read_tool = ReadFileTool()
    assert read_tool.name == "read_file"
    assert read_tool.description
    
    definition = read_tool.get_definition()
    assert "name" in definition
    assert "description" in definition
    assert "parameters" in definition
    
    print("✓ ReadFileTool definition OK")
    
    # Write tool
    write_tool = WriteFileTool()
    assert write_tool.name == "write_file"
    
    definition = write_tool.get_definition()
    assert definition["parameters"]["required"] == ["path", "content"]
    
    print("✓ WriteFileTool definition OK")
    
    # Command tool
    cmd_tool = ExecuteCommandTool()
    assert cmd_tool.name == "execute_command"
    assert len(cmd_tool.BLOCKED_COMMANDS) > 0
    
    print("✓ ExecuteCommandTool definition OK")
    
    print("\n✅ All tool definitions are valid!")


if __name__ == "__main__":
    test_tool_definitions()
