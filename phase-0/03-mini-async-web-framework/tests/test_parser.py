from http.parser import HttpParser


def test_parse_get_request():

    raw = (
        b"GET /hello HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"Connection: close\r\n"
        b"\r\n"
    )

    request = HttpParser.parse(raw)

    assert request.method == "GET"
    assert request.path == "/hello"
    assert request.version == "HTTP/1.1"
    assert request.headers["Host"] == "localhost"
    assert request.headers["Connection"] == "close"

"""
python -m pytest tests/test_parser.py
"""