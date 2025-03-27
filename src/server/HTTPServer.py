import asyncio
import mimetypes
import os
from pathlib import Path

from src.cache.FileCache import FileCache
from src.server.HTTPRequest import HTTPRequest
from src.server.HTTPResponse import HTTPResponse
from src.server.ServerConfig import ServerConfig


class HTTPServer:
    """Асинхронный HTTP-сервер."""
    def __init__(self, config: ServerConfig):
        self.config = config
        self.file_cache = FileCache(max_size=config.open_file_cache_max_size)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Обработка клиентского соединения."""
        request_data = await reader.read(4096)
        request = HTTPRequest(request_data)

        if request.method == 'GET':
            await self.handle_get_request(request, writer)
        else:
            await self.handle_unsupported_method(writer)

        writer.close()
        await writer.wait_closed()

    async def handle_get_request(self, request: HTTPRequest,
                                 writer: asyncio.StreamWriter):
        """Обработка GET-запроса."""
        path = request.path
        if path == '/':
            path = '/index.html'

        # Удаляем начальный слэш и проверяем переходы наверх
        safe_path = path.lstrip('/')
        if '..' in safe_path:
            response = HTTPResponse(
                status_code=403,
                content_type='text/plain',
                content_length=23,
                body=b"403 Forbidden (Path Traversal)"
            )
            writer.write(response.build_response())
            await writer.drain()
            return

        # Полный путь к файлу
        file_path = Path(self.config.static_dir) / safe_path

        if file_path.is_file():
            try:
                if self.config.open_file_cache_enabled:
                    cached_file = self.file_cache.get_file(file_path)
                    if cached_file:
                        file_descriptor, file_size, last_modified = cached_file
                    else:
                        response = HTTPResponse(
                            status_code=503,
                            content_type='text/plain',
                            content_length=19,
                            body=b"503 Cache Overflow"
                        )
                        writer.write(response.build_response())
                        await writer.drain()
                        return
                else:
                    file_descriptor = open(file_path, 'rb')
                    file_size = os.path.getsize(file_path)
                    last_modified = os.path.getmtime(file_path)

                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                # Читаем файл
                file_descriptor.seek(0)
                file_content = file_descriptor.read()

                # Если не из кэша - закрываем файл
                if not self.config.open_file_cache_enabled:
                    file_descriptor.close()

                response = HTTPResponse(
                    status_code=200,
                    content_type=mime_type,
                    content_length=file_size,
                    body=file_content
                )
                writer.write(response.build_response())
            except Exception as e:
                print(f"Error serving file: {e}")
                response = HTTPResponse(
                    status_code=500,
                    content_type='text/plain',
                    content_length=25,
                    body=b"500 Internal Server Error"
                )
                writer.write(response.build_response())
        else:
            response = HTTPResponse(
                status_code=404,
                content_type='text/html',
                content_length=13,
                body=b"404 Not Found"
            )
            writer.write(response.build_response())

        await writer.drain()

    async def handle_unsupported_method(self, writer: asyncio.StreamWriter):
        """Обработка неподдерживаемых методов."""
        response = HTTPResponse(
            status_code=405,
            content_type='text/plain',
            content_length=18,
            body=b"405 Method Not Allowed"
        )
        writer.write(response.build_response())
        await writer.drain()

    async def start(self):
        """Запуск сервера."""
        server = await asyncio.start_server(self.handle_client, self.config.host, self.config.port)
        print(f"Сервер запущен на {self.config.host}:{self.config.port}")
        async with server:
            await server.serve_forever()

    def stop(self):
        """Закрытие сервера и очистка ресурсов."""
        print("Сервер остановлен")
        self.file_cache.close_all()