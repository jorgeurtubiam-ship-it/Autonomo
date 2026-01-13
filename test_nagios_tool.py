import asyncio
import aiohttp
from backend.tools.nagios_tools import NagiosTool

async def test():
    tool = NagiosTool()
    # Usar credenciales del usuario
    result = await tool.execute(
        url="http://localhost:8080/nagios",
        user="nagiosadmin",
        password="nagios@2025"
    )
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test())
