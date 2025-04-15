import asyncio
import os

from src.server.HTTPServer import HTTPServer
from src.server.ServerConfig import ServerConfig


async def main():
    config_path = os.path.join(os.path.dirname(__file__), "server.json")
    config = ServerConfig(config_path)
    server = HTTPServer(config)
    try:
        await server.start()
    except asyncio.CancelledError:
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())
