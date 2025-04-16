from src.server.HTTPRequest import HTTPRequest


def test_parse_basic_request():
    request_data = b"GET /test?param=value HTTP/1.1\r\nHost: localhost\r\n\r\n"
    request = HTTPRequest(request_data)

    assert request.method == "GET"
    assert request.path == "/test"
    assert request.query_params["param"][0] == "value"
    assert request.headers["Host"] == "localhost"


def test_parse_request_with_encoding():
    request_data = b"GET /%D0%BF%D1%83%D1%82%D1%8C HTTP/1.1\r\n"
    request = HTTPRequest(request_data)
    assert request.path == "/путь"


def test_empty_request():
    request = HTTPRequest(b"")
    assert request.method is None
    assert request.path is None