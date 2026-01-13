"""
Ejemplo: Test de Tools Individuales
Prueba cada tool por separado
"""

import asyncio
from tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    ExecuteCommandTool,
    GitStatusTool
)


async def test_file_tools():
    """Test de tools de archivos"""
    print("=" * 60)
    print("TEST: File Tools")
    print("=" * 60)
    
    # Write file
    write_tool = WriteFileTool()
    result = await write_tool.execute(
        path="test_example.txt",
        content="Este es un archivo de prueba\nCon múltiples líneas\n¡Hola mundo!"
    )
    print(f"\n✓ write_file: {result}")
    
    # Read file
    read_tool = ReadFileTool()
    result = await read_tool.execute(path="test_example.txt")
    print(f"\n✓ read_file: {result}")
    
    # List directory
    list_tool = ListDirectoryTool()
    result = await list_tool.execute(path=".")
    print(f"\n✓ list_directory: Encontrados {result.get('total')} items")
    for item in result.get('items', [])[:5]:  # Primeros 5
        print(f"  - {item['name']} ({item['type']})")


async def test_command_tools():
    """Test de tools de comandos"""
    print("\n" + "=" * 60)
    print("TEST: Command Tools")
    print("=" * 60)
    
    # Execute command
    cmd_tool = ExecuteCommandTool()
    result = await cmd_tool.execute(command="echo 'Hola desde el agente'")
    print(f"\n✓ execute_command:")
    print(f"  stdout: {result.get('stdout')}")
    print(f"  success: {result.get('success')}")


async def test_git_tools():
    """Test de tools de Git"""
    print("\n" + "=" * 60)
    print("TEST: Git Tools")
    print("=" * 60)
    
    # Git status
    git_tool = GitStatusTool()
    result = await git_tool.execute(path=".")
    print(f"\n✓ git_status:")
    print(f"  success: {result.get('success')}")
    if result.get('success'):
        files = result.get('files', {})
        print(f"  modified: {len(files.get('modified', []))}")
        print(f"  untracked: {len(files.get('untracked', []))}")


async def main():
    """Ejecuta todos los tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║              TEST DE TOOLS INDIVIDUALES                  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    await test_file_tools()
    await test_command_tools()
    await test_git_tools()
    
    print("\n✅ Tests completados!")


if __name__ == "__main__":
    asyncio.run(main())
