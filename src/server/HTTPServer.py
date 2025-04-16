import asyncio
import html
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
        self.routes = {
            '/greet': self.handle_greet_page,
            '/calculator': self.handle_calculator
        }
        self.template_dir = Path(config.static_dir) / "templates"

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

    async def handle_get_request(self, request: HTTPRequest, writer: asyncio.StreamWriter):
        """Обработка GET-запроса."""
        handler = self.routes.get(request.path)
        if handler:
            await handler(request, writer)
            return

        path = request.path
        if path == '/':
            path = '/index.html'

        safe_path = path.lstrip('/')
        if '..' in safe_path:
            await self.handle_error(403, writer)
            return

        file_path = Path(self.config.static_dir) / safe_path

        if file_path.is_file():
            try:
                if self.config.open_file_cache_enabled:
                    cached_file = self.file_cache.get_file(file_path)
                    if cached_file:
                        file_descriptor, file_size, last_modified = cached_file
                    else:
                        await self.handle_error(503, writer)
                        return
                else:
                    file_descriptor = open(file_path, 'rb')
                    file_size = os.path.getsize(file_path)
                    last_modified = os.path.getmtime(file_path)

                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'

                file_descriptor.seek(0)
                file_content = file_descriptor.read()

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
                await self.handle_error(500, writer)
        else:
            await self.handle_error(404, writer)

        await writer.drain()

    async def handle_unsupported_method(self, writer: asyncio.StreamWriter):
        """Обработка неподдерживаемых методов."""
        await self.handle_error(405, writer)

    async def _render_template(self, template_name: str,
                               context: dict) -> bytes:
        """Рендер HTML-шаблона с контекстом."""
        template_path = self.template_dir / template_name

        try:
            if self.config.open_file_cache_enabled:
                cached = self.file_cache.get_file(template_path)
                if cached:
                    fd, size, _ = cached
                    content = fd.read().decode('utf-8')
                else:
                    return None
            else:
                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read()

            for key, value in context.items():
                content = content.replace(f"{{{{{key}}}}}", value)

            return content.encode('utf-8')

        except Exception as e:
            print(f"Template error: {e}")
            return None

    async def handle_greet_page(self, request: HTTPRequest,
                                writer: asyncio.StreamWriter):
        """Обработка страницы приветствия."""
        name = html.escape(request.query_params.get('name', ['Гость'])[0])

        params_html = "".join(
            f"<li><strong>{html.escape(k)}:</strong> {html.escape(v[0])}</li>"
            for k, v in request.query_params.items()
        )

        context = {
            "name": name,
            "params": params_html
        }

        content = await self._render_template("greet_template.html", context)

        if not content:
            await self.handle_error(500, writer)
            return

        response = HTTPResponse(
            status_code=200,
            content_type='text/html; charset=utf-8',
            content_length=len(content),
            body=content
        )
        writer.write(response.build_response())
        await writer.drain()

    async def handle_calculator(self, request: HTTPRequest, writer: asyncio.StreamWriter):
        """Простой калькулятор"""
        try:
            a = request.query_params.get('a', ['0'])[0]
            b = request.query_params.get('b', ['0'])[0]
            op = request.query_params.get('op', ['add'])[0]

            safe_a = html.escape(a)
            safe_b = html.escape(b)
            safe_op = html.escape(op)

            operations = {
                'add': ('+', lambda x, y: x + y),
                'sub': ('-', lambda x, y: x - y),
                'mul': ('×', lambda x, y: x * y),
                'div': ('÷', lambda x, y: x / y)
            }

            try:
                a_num = float(safe_a)
                b_num = float(safe_b)
            except ValueError:
                await self.handle_error(400, writer)
                return

            if op not in operations:
                await self.handle_error(400, writer)
                return

            op_symbol, operation = operations[op]

            try:
                result = operation(a_num, b_num)
            except ZeroDivisionError:
                result = "Ошибка: деление на ноль"

            context = {
                "a": safe_a,
                "b": safe_b,
                "op_symbol": op_symbol,
                "result": html.escape(str(result))
            }

            content = await self._render_template("calculator_template.html",
                                                  context)

            if not content:
                raise Exception("Ошибка загрузки шаблона")

        except Exception as e:
            await self.handle_error(500, writer, str(e))
            return

        response = HTTPResponse(
            status_code=200,
            content_type='text/html; charset=utf-8',
            content_length=len(content),
            body=content
        )
        writer.write(response.build_response())
        await writer.drain()

    async def handle_error(self, status_code: int, writer: asyncio.StreamWriter):
        """Формирование ответа с ошибкой."""
        error_page = Path(self.config.static_dir) / f"{status_code}.html"
        content_type = "text/html"
        body = None

        try:
            if error_page.is_file():
                with open(error_page, "rb") as file:
                    body = file.read()
                content_length = len(body)
            else:
                default_message = f"{status_code} {HTTPResponse.get_status_message(status_code)}".encode()
                content_type = "text/plain"
                body = default_message
                content_length = len(body)
        except Exception as e:
            print(f"Error loading error page: {e}")
            default_message = f"{status_code} {HTTPResponse.get_status_message(status_code)}".encode()
            content_type = "text/plain"
            body = default_message
            content_length = len(body)

        response = HTTPResponse(
            status_code=status_code,
            content_type=content_type,
            content_length=content_length,
            body=body
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