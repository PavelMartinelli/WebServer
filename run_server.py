import asyncio
from src.server.HTTPServer import HTTPServer
from src.server.ServerConfig import ServerConfig


async def main():
    config = ServerConfig("server.conf")
    server = HTTPServer(config)
    try:
        await server.start()
    except asyncio.CancelledError:
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())
