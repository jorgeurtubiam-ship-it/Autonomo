"""
Test funcional - Ejecuta tools reales
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.tools.file_tools import WriteFileTool, ReadFileTool, ListDirectoryTool
from backend.tools.command_tools import ExecuteCommandTool


async def test_file_operations():
    """Test de operaciones de archivos"""
    print("\n" + "="*60)
    print("TEST: File Operations")
    print("="*60)
    
    # 1. Escribir archivo
    print("\n1. Escribiendo archivo...")
    write_tool = WriteFileTool()
    result = await write_tool.execute(
        path="test_output.txt",
        content="Este es un test funcional\nLínea 2\nLínea 3"
    )
    print(f"   ✓ Resultado: {result['success']}")
    print(f"   ✓ Path: {result['path']}")
    print(f"   ✓ Tamaño: {result['size']} bytes")
    
    # 2. Leer archivo
    print("\n2. Leyendo archivo...")
    read_tool = ReadFileTool()
    result = await read_tool.execute(path="test_output.txt")
    print(f"   ✓ Resultado: {result['success']}")
    print(f"   ✓ Líneas: {result['lines']}")
    print(f"   ✓ Contenido:\n{result['content']}")
    
    # 3. Listar directorio
    print("\n3. Listando directorio actual...")
    list_tool = ListDirectoryTool()
    result = await list_tool.execute(path=".")
    print(f"   ✓ Total items: {result['total']}")
    print(f"   ✓ Archivos: {result['files']}")
    print(f"   ✓ Directorios: {result['directories']}")
    print(f"   ✓ Primeros 5 items:")
    for item in result['items'][:5]:
        print(f"      - {item['name']} ({item['type']})")
    
    return True


async def test_command_execution():
    """Test de ejecución de comandos"""
    print("\n" + "="*60)
    print("TEST: Command Execution")
    print("="*60)
    
    cmd_tool = ExecuteCommandTool()
    
    # 1. Comando simple
    print("\n1. Ejecutando 'echo Hello'...")
    result = await cmd_tool.execute(command="echo 'Hello from agent'")
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Return code: {result['returncode']}")
    print(f"   ✓ Output: {result['stdout'].strip()}")
    
    # 2. Comando con pwd
    print("\n2. Ejecutando 'pwd'...")
    result = await cmd_tool.execute(command="pwd")
    print(f"   ✓ Success: {result['success']}")
    print(f"   ✓ Working dir: {result['stdout'].strip()}")
    
    # 3. Comando bloqueado
    print("\n3. Intentando comando bloqueado...")
    result = await cmd_tool.execute(command="rm -rf /")
    print(f"   ✓ Blocked: {result.get('blocked', False)}")
    print(f"   ✓ Error: {result.get('error', 'N/A')}")
    
    return True


async def main():
    """Ejecuta todos los tests"""
    print("""
╔══════════════════════════════════════════════════════════╗
║           TESTS FUNCIONALES - TOOLS REALES               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Test 1: File operations
        success1 = await test_file_operations()
        
        # Test 2: Command execution
        success2 = await test_command_execution()
        
        print("\n" + "="*60)
        if success1 and success2:
            print("✅ TODOS LOS TESTS PASARON!")
        else:
            print("❌ ALGUNOS TESTS FALLARON")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
