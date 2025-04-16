from src.server.HTTPResponse import HTTPResponse


def test_response_building():
    response = HTTPResponse(
        status_code=200,
        content_type="text/plain",
        content_length=11,
        body=b"Hello World"
    )
    result = response.build_response()

    assert b"HTTP/1.1 200 OK" in result
    assert b"Content-Type: text/plain" in result
    assert b"Content-Length: 11" in result
    assert b"Hello World" in result


def test_status_message():
    assert HTTPResponse.get_status_message(404) == "Not Found"
    assert HTTPResponse.get_status_message(999) == "Unknown Status"