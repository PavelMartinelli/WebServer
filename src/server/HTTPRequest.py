class HTTPRequest:
    """Класс для разбора HTTP-запроса."""
    def __init__(self, request_data: bytes):
        self.method = None
        self.path = None
        self.headers = {}
        self.parse_request(request_data)

    def parse_request(self, request_data: bytes):
        """Разбор HTTP-запроса."""
        request_lines = request_data.decode().splitlines()
        if not request_lines:
            return

        # Разбор первой строки (метод, путь, версия протокола)
        self.method, self.path, _ = request_lines[0].split()

        # Разбор заголовков
        for line in request_lines[1:]:
            if not line.strip():
                break
            key, value = line.split(':', 1)
            self.headers[key.strip()] = value.strip()
