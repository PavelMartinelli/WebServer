from urllib.parse import unquote, parse_qs


class HTTPRequest:
    """Класс для разбора HTTP-запроса."""

    def __init__(self, request_data: bytes):
        self.method = None
        self.path = None
        self.query_params = {}
        self.headers = {}
        self.parse_request(request_data)

    def parse_request(self, request_data: bytes):
        """Разбор HTTP-запроса."""
        request_lines = request_data.decode().splitlines()
        if not request_lines:
            return

        first_line = request_lines[0].split()
        if len(first_line) < 3:
            return

        self.method, full_path, _ = first_line

        path_parts = full_path.split('?', 1)
        self.path = unquote(path_parts[0])

        if len(path_parts) > 1:
            query_string = path_parts[1]
            self.query_params = parse_qs(query_string)

        for line in request_lines[1:]:
            if not line.strip():
                break
            key, value = line.split(':', 1)
            self.headers[key.strip()] = value.strip()
