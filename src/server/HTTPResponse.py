class HTTPResponse:
    """Класс для формирования HTTP-ответа."""
    def __init__(self, status_code: int, content_type: str, content_length: int, body: bytes = None):
        self.status_code = status_code
        self.content_type = content_type
        self.content_length = content_length
        self.body = body

    def build_response(self) -> bytes:
        """Сформировать HTTP-ответ."""
        response_headers = [
            f"HTTP/1.1 {self.status_code} {self.get_status_message(self.status_code)}",
            f"Content-Type: {self.content_type}",
            f"Content-Length: {self.content_length}",
            "Connection: keep-alive",
            "\r\n"
        ]
        response = "\r\n".join(response_headers).encode()
        if self.body:
            response += self.body
        return response

    @staticmethod
    def get_status_message(status_code: int) -> str:
        """Получить текстовое описание статуса."""
        status_messages = {
            200: "OK",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
            503: "Service Unavailable"
        }
        return status_messages.get(status_code, "Unknown Status")