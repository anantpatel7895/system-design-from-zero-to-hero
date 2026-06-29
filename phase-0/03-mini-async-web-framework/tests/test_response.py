from http.response import Response


def test_json_response():

    response = Response(
        {
            "message": "hello"
        }
    )

    raw = response.to_bytes()

    assert b"HTTP/1.1 200 OK" in raw

    assert b"application/json" in raw

    assert b'"message": "hello"' in raw